import getpass

from fabric.api import *
from fabric.colors import green, red
from fabric.context_managers import prefix
from fabric.operations import sudo


env.project_name = 'pywars'

#def dev():
#    """This pushes to localhost dev environment"""
#    env.hosts = ['localhost']
#    env.user = 'pywars'
#    env.code_root = '/home/pywars/environment'

def prd():
    """This pushes to the intranet prd environment"""
    env.hosts = ['pyconar.onapsis.com']
    env.user = 'pywars'
    env.code_root = '/home/pywars/environment'

def test():
    """This pushes to the intranet test environment"""
    env.hosts = ['172.16.100.172']
    env.user = 'pywars'
    env.code_root = '/home/pywars/environment'

def clean_db():
    require('hosts')
    with settings(warn_only=True):
        run('cd %s/releases/current/pywars/pywars/; rm database.sqlite' % (env.code_root,))

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts')
    sudo('apt-get install -y python-setuptools')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('apt-get install -y apache2')
    sudo('apt-get install -y libapache2-mod-wsgi')
    sudo('apt-get install -y libcurl4-openssl-dev')
    sudo('apt-get install -y rabbitmq-server')
    sudo('apt-get install -y python-dev')
    sudo('apt-get install -y libyaml-dev')
    sudo('apt-get install -y build-essential')
    sudo('apt-get install -y git')
    sudo('apt-get install -y npm nodejs-legacy')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y python-pypy.sandbox')
    sudo('npm install -g bower')
    with settings(warn_only=True):
        sudo('mkdir -p %s' % env.code_root)
    sudo('cd %s; virtualenv .;source ./bin/activate' % env.code_root)
    reset_permissions()

    with settings(warn_only=True):
        # we want rid of the default apache config
        sudo('a2enmod wsgi;')
        sudo('a2dissite default;')
        sudo('a2dissite 000-default;')
        sudo('mkdir -p /etc/supervisor/conf.d')
        run('cd %s; mkdir releases; mkdir shared; mkdir packages;' % (env.code_root))
    #install_mysql()

def setup_rabbitmq():
    with settings(warn_only=True):
        rabbit_pass = getpass.getpass(prompt='Choose a password for rabbitmq user pywars:')
        sudo('rabbitmqctl add_user pywars %s' % rabbit_pass)
        sudo('rabbitmqctl add_vhost pywarsvhost')
        sudo('rabbitmqctl set_permissions -p pywarsvhost pywars ".*" ".*" ".*"')
        sudo('mkdir -p /etc/rabbitmq/ssl/ca')
        sudo('mkdir /etc/rabbitmq/ssl/server')

def start_rabbitmq():
    sudo('sudo service rabbitmq-server start', pty=False)

def stop_rabbitmq():
    sudo('sudo service rabbitmq-server stop', pty=False)

def install_mysql():
    """ Installs MySQL database engine """
    sudo('apt-get -y install libmysqlclient-dev')
    sql_pw = getpass.getpass(prompt='Create MySQL root password (blank for none):')
    sql_pw_repeat = getpass.getpass(prompt='Repeat root password:')
    while sql_pw != sql_pw_repeat:
        sql_pw = getpass.getpass(prompt='Passwords do not match.\n\
                                 Enter root password (blank for none):')
        sql_pw_repeat = getpass.getpass(prompt='Repeat root password:')
    sudo('DEBIAN_FRONTEND=noninterfactive apt-get -y install mysql-server')
    if len(sql_pw) is not 0:
        sudo('mysqladmin -u root password {0}'.format(sql_pw))

def remove_db():
    root_pw = getpass.getpass(prompt='MySQL root password:')
    run('mysql -u root -p%s -e "DROP DATABASE IF EXISTS db_%s"' % (root_pw, env.project_name))
    with settings(warn_only=True):
        run('mysql -u root -p%s -e "DROP USER \'%s\'@\'localhost\'"' % (root_pw, env.project_name))

def create_db():
    """ Creates new schema & user to manage it """
    root_pw = getpass.getpass(prompt='MySQL root password:')
    # Create new DB
    run('mysql -u root -p{0} -e "CREATE DATABASE db_{1}"'.format(root_pw, env.project_name))
    db_pw = getpass.getpass(prompt='Create DB user password:')
    db_pw_repeat = getpass.getpass(prompt='Repeat password:')

    while db_pw != db_pw_repeat:
        db_pw = getpass.getpass(prompt='Passwords do not match.\nCreate DB user password:')
        db_pw_repeat = getpass.getpass(prompt='Repeat password:')

    # Create user to administer the DB
    run('mysql -u root -p{0} -e "CREATE USER \'{1}\'@\'localhost\' IDENTIFIED BY \'{2}\'"'\
    .format(root_pw, env.project_name, db_pw))
    # Grant user permissions
    run('mysql -u root -p{0} -e "GRANT ALL PRIVILEGES ON db_{1}.* TO \'{1}\'@\'localhost\'"'\
    .format(root_pw, env.project_name))
    run('mysql -u root -p{0} -e "FLUSH PRIVILEGES"'.format(root_pw))

def reset_permissions():
    sudo('chown %s -R %s' % (env.user, env.code_root))
    sudo('chgrp %s -R %s' % (env.user, env.code_root))

def push_code():
    require('hosts')
    require('code_root')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    tar_file = '%s.tar.gz' % (env.release,)

    local('git archive --format=tar develop | gzip > %s' % (tar_file,))

    put(tar_file, '%s/packages/' % env.code_root)

    run('mkdir -p %s/releases/%s/pywars' % (env.code_root, env.release))
    run('cd %s/releases && tar zxf ../packages/%s.tar.gz -C %s/releases/%s/pywars' % (env.code_root, env.release, env.code_root, env.release))
    with prefix('source %s/bin/activate' % (env.code_root,)):
        run("cd %s/releases/%s/pywars; pip install -r requirements.txt" % (env.code_root, env.release))
        run('cd %s/releases/%s/pywars; pip install mysql-python')
        run('cd %s/releases/%s/pywars; python manage.py bower install' % (env.code_root, env.release))
        run("cd %s/releases/%s/pywars; python manage.py collectstatic --noinput" % (env.code_root, env.release))

    local('rm -fr %s' % (env.release,))
    local('rm %s' % (tar_file,))
    symlink_current_release()
    with settings(warn_only=True):
        # copy the local_settings for deployment
        run("cp /home/%s/local_settings.py %s/releases/%s/pywars/battleground/" % (env.user, env.code_root, env.release))
    with prefix('source %s/bin/activate' % (env.code_root,)):
        run("cd %s/releases/%s/pywars; python manage.py migrate" % (env.code_root, env.release))

def symlink_current_release():
    "Symlink our current release"
    require('release')
    with settings(warn_only=True):
        run('cd %s; rm releases/previous; mv releases/current releases/previous;' % (env.code_root,))
    run('cd %s; ln -s %s releases/current' % (env.code_root, env.release))

"""def load_initial_db():
    require('hosts')
    with prefix('source %s/bin/activate' % (env.code_root,)):
        run("cd %s/releases/current; python pywars/manage.py loaddata initial" % (env.code_root,))

def load_backup_db():
    require('hosts')
    with prefix('source %s/bin/activate' % (env.code_root,)):
        run("cd %s/releases/current; python pywars/manage.py loaddata backup_v1" % (env.code_root,))
    """

def deploy():
    require('hosts')
    require('code_root')
    print(red("Beginning Deploy:"))
    stop_supervisord()
    push_code()
    symlink_current_release()
    install_apache_site()
    install_supervisord()
    restart_apache()
    start_supervisord()
    print(green("Deployment finished"))

def down():
    require('hosts')
    require('code_root')
    run('cd %s/releases/current/pywars/pywars/; touch down' % (env.code_root,))

def up():
    require('hosts')
    require('code_root')
    run('cd %s/releases/current/pywars/pywars/; rm down' % (env.code_root,))

def install_apache_site():
    "Add the virtualhost file to apache"
    env.user = 'pywars'
    sudo('cd %s/releases/current/pywars; cp conf/%s.conf /etc/apache2/sites-available/; cp battleground/wsgi.py /var/www/pywars.wsgi' % (env.code_root, env.project_name))
    with settings(warn_only=True):
        sudo('cd /etc/apache2/; mkdir ssl;')
        sudo('mkdir -p /var/www/static')
        sudo('chown -R pywars:www-data /var/www/')
        # copy the ssl certificates
        # sudo('cd ~; cp apache/partner.onapsis.com.crt /etc/apache2/ssl')
        # sudo('cd ~; cp apache/partner.onapsis.com.key /etc/apache2/ssl')
        # sudo('cd ~; cp apache/rapidssl_intermediate_ca.crt /etc/apache2/ssl')

    sudo('a2ensite %s' % (env.project_name,))
    sudo('a2enmod ssl')
    sudo('a2enmod rewrite')
    with settings(warn_only=True):
        sudo('mkdir /var/log/apache2/%s' % (env.project_name,))

def create_ssl_certs():
    require('hosts')
    with settings(warn_only=True):
        sudo('openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/apache.key -out /etc/apache2/ssl/apache.crt')

def install_supervisord():
    require('hosts')
    with settings(warn_only=True):
        #sudo('cd %s/releases/current/pywars; cp supervisord.conf /etc/supervisor/supervisord.conf' % (env.code_root,))
        sudo('cd %s/releases/current/pywars; cp conf/celery.conf /etc/supervisor/conf.d' % (env.code_root,))

def start_supervisord():
    require('hosts')
    with prefix('source %s/bin/activate' % (env.code_root,)):
        sudo('supervisord -c /etc/supervisor/supervisord.conf')

def stop_supervisord():
    with settings(warn_only=True):
        sudo('supervisorctl -c /etc/supervisor/supervisord.conf shutdown')

def stop_apache():
    "Restart the web server"
    env.user = "pywars"
    sudo('service apache2 stop', pty=False)

def start_apache():
    "Restart the web server"
    env.user = "pywars"
    sudo('service apache2 start', pty=False)

def restart_apache():
    "Restart the web server"
    env.user = "pywars"
    sudo('service apache2 stop')
    sudo('service apache2 start', pty=False)

def touch_wsgi():
    "Touching wsgi will cause apache to update the code without restart"
    run("cd %s/releases/current; touch django.wsgi" % (env.code_root,))
