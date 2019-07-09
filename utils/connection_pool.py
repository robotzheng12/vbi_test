class ConnectionPool(object):
    """
    连接池
    """

    def __init__(self, number):
        self.pool = []

    def pop(self):
        """
        从连接池取出一个连接
        :return:
        """
        return self.pool.pop()

    def push(self, connectionObj):
        """
        放回一条连接
        :return:
        """
        self.pool.append(connectionObj)
        pass
