import logging
from abc import ABC, abstractmethod
from itertools import chain
from typing import Union

logger = logging.getLogger()


class Node:
    def __init__(self, parent: Union["Node", None] = None):
        self.parent = parent
        self._children = []

    @property
    def parent(self):
        if hasattr(self, '_parent'):
            return self._parent
        return

    @parent.setter
    def parent(self, value: Union[None, "Node"]):
        if value is not None and not isinstance(value, Node):
            logger.exception(f'Parent node {value} is not of type TreeNode')
            raise ValueError(f'Parent node {value} is not of type TreeNode')

        parent = self.parent
        if parent is not value:
            if value is not None:
                self.check_loop(value)
            if parent is not None:
                parent._children = [child for child in parent._children if child is not self]
            if value is not None:
                value._children.append(self)
                self._parent = value

    def check_loop(self, node: "Node"):
        if node is self or any(child is self for child in node.reverse()):
            logger.exception(f'{node}, Cannot set parent, {self.parent}, Loop Error')
            raise ValueError('Cannot set parent. Loop Error')

    def clear(self):
        for child in self._children:
            child.clear()
        self.parent = None

    def reverse(self):
        node = self
        while node is not None:
            yield node
            node = node.parent


class TreeIter(ABC):
    @abstractmethod
    def __init__(self):
        self._children = []

    def __iter__(self):
        yield from chain(*self._children)
        yield self


class TreeUi(Node, TreeIter):
    def __init__(self, name: str, ui_builder: object, parent: Union[None, Node] = None):
        super().__init__(parent)
        self.name = name
        self.builder = ui_builder

    @property
    def root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def find(self, name: str):
        for node in self.root:
            if node.name == name:
                return node
        return
