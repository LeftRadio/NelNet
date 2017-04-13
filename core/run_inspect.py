# python3!

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph.output import GraphvizOutput

from nelnet import _nelnet_test
# from hal.vcom_usart import _vcom_test


def main():
    """ """
    config = Config(groups=True, threaded=False)

    graphviz = GraphvizOutput()
    graphviz.output_file = 'nelnet_test_callgraph.png'

    with PyCallGraph(output=graphviz, config=config):
        _nelnet_test()


if __name__ == '__main__':
    """ """
    main()
