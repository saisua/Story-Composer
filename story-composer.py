import core
import logging, wx

# Main function for testing
def main():
    # level = logging. + [CRITICAL, ERROR, WARNING, INFO, DEBUGGING]
    logging.basicConfig(format='%(asctime)s %(levelname)s | %(message)s', level=logging.DEBUG)

    app = wx.App()

    seq = core.Sequence_editor(name="Story Composer",num_columns=5)

    app.MainLoop()

if __name__ == "__main__":
    main()