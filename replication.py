from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class VersionVector:
    value: list[int]

    def increment(self, node_i: int):
        return VersionVector([version + 1 if node_i == i else version for i, version in enumerate(self.value)])

    def happens_before(self, other: VersionVector):
        return all(a <= b for a, b in zip(self.value, other.value))
    
    @staticmethod
    def merge(a: VersionVector, b: VersionVector):
        return VersionVector([max(a, b) for a, b in zip(a.value, b.value)])
    
    def __hash__(self):
        return hash(x for x in self.value)
    
    def __repr__(self):
        return f'VersionVector({str(self.value)})'


@dataclass(frozen=True)
class VersionedElement:
    value: str
    version: VersionVector

    def __repr__(self):
        return self.value


@dataclass(frozen=True)
class OrSet:
    add_set: set[VersionedElement]
    remove_set: set[VersionedElement]
    version: VersionVector

    @property
    def visible_set(self):
        result = set()
        for add_item in self.add_set:
            ok = True
            for remove_item in self.remove_set:
                if add_item.value == remove_item.value:  # items are equal!
                    if add_item.version.happens_before(remove_item.version):  # adds win over removes
                        ok = False
                        break
            if ok:
                result.add(add_item)
        return result
    
    def add(self, value: str, i: int):
        new_version = self.version.increment(i)
        return OrSet(self.add_set | {VersionedElement(value, new_version)}, self.remove_set, new_version)
    
    def remove(self, value: str, i: int):
        new_version = self.version.increment(i)
        return OrSet(self.add_set, self.remove_set | {VersionedElement(value, new_version)}, new_version)
    
    @staticmethod
    def merge(a: OrSet, b: OrSet):
        # no compression of redundant elements here
        return OrSet(a.add_set | b.add_set, a.remove_set | b.remove_set, VersionVector.merge(a.version, b.version))

    def __repr__(self):
        return str(self.visible_set)


class Node:
    def __init__(self, nodes_n: int, node_i: int):
        self.i: int = node_i
        self.states: list[OrSet] = [OrSet(set(), set(), VersionVector([0 for _ in range(nodes_n)]))]

    def read(self):
        return self.states[-1]

    def write(self, value: OrSet):
        self.states.append(value)

    def sync(self, other: Node):
        print()
        print(f'Syncing {self.i} with {other.i} | versions: {self.read().version} & {other.read().version}')
        print(f'                 |    state: {self.read()} & {other.read()}')

        if self.read().version == other.read().version:
            print(f'                 | nodes are equal')

        elif self.read().version.happens_before(other.read().version):
            print(f'                 | {self.i} is outdated')
            self.states.append(other.read())

        elif other.read().version.happens_before(self.read().version):
            print(f'                 | {other.i} is outdated')
            other.states.append(self.read())

        else:
            self._merge_conflicts(other)
            print('                 | nodes are concurrent')

        print()
    
    def _merge_conflicts(self, other: Node):
        merged = OrSet.merge(self.read(), other.read())
        self.states.append(merged)
        other.states.append(merged)

        print(f'                 |   merged: {self.read().visible_set}')


class Client:
    def __init__(self, name: str, nodes_n: int):
        self.name = name
    
    def write_add(self, node: Node, value: str):
        latest = node.read()
        new_value = latest.add(value, node.i)
        node.write(new_value)

        print(f'{self.name}: add {value}, write {new_value} to node {node.i} with {latest.version}')

    def write_remove(self, node: Node, value: str):
        latest = node.read()
        new_value = latest.remove(value, node.i)
        node.write(new_value)

        print(f'{self.name}: remove {value}, write {new_value} to node {node.i} with {latest.version}')
