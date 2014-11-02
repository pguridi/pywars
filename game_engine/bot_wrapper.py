import sys
import importlib


def main(bot_file):
    bot_file = bot_file[0].replace(".py", "")
    i = importlib.import_module(bot_file)
    bot = i.Bot()

    while True:
        c = raw_input()
        if c == "END":
            break
        else:
            print bot.execute(c)
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please add the bot filename as parameter"
        sys.exit(1)
    main(sys.argv[1:])