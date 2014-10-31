# encoding=utf-8

from game_engine.security import seal
from multiprocessing import Process, Queue, current_process
from Queue import Empty
import inspect
import traceback


class RemoteInstance(object):

    class Timeout(Exception): pass

    class InvalidOutput(Exception): pass

    def __init__(self, klass, timeout=.1, namespace=None, validator=None, *args, **kwargs):
        self.timeout = timeout
        self.qin = Queue()
        self.qout = Queue()
        self.proc = Process(target=self.worker, args=(klass, self.qout, self.qin, namespace, validator))
        self.proc.start()

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            try:
                try:
                    #print current_process(), 'Calling %s(...)' % name
                    self.qout.put([name, args, kwargs])
                    result = self.qin.get(timeout=self.timeout)
                    #print current_process(),'RECEIVED:',result
                    return result
                except Empty:
                    # Translate Queue.Emtpy into our own exception
                    raise self.Timeout()
            except:
                self.proc.terminate()
                raise
        return wrapper

    @staticmethod
    def worker(klass, input, output, namespace=None, class_validator=None):
        try:
            seal() # seal the running environment, EXTERMINATE! EXTERMINATE sys!
            if isinstance(klass, basestring):  # Received a string of code
                if class_validator is None:
                    class_validator = lambda x: True
                namespace = namespace or {}
                exec klass in namespace
                # Find the first class declared in our custom namespace
                klass = [var for var in namespace.values() if inspect.isclass(var) and class_validator(var)][0]
            #print current_process(), 'Instancing %s' % klass
            instance = klass()
            for method, args, kwargs in iter(input.get, 'STOP'):
                #print current_process(), 'Calling %s(...)' % method
                result = getattr(instance, method)(*args, **kwargs)
                #print current_process(), 'Result:',result
                output.put(result)
        except Exception as ex:
            desc = traceback.format_exc()
            desc = '\n'.join([line for line in desc.split('\n') if '/home' not in line and '/var' not in line])
            print 'Error running bot (%s)' % str(desc)
            output.put(Exception(desc))
            raise

    def terminate(self):
        self.proc.terminate()
