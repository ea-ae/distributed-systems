from replication import Node, Client


def simulate():
    NODES_N = 2

    zero = Node(NODES_N, 0)
    one = Node(NODES_N, 1)
    # two = Node(NODES_N, 2)

    alice = Client('Alice', NODES_N)
    bob = Client('Bobby', NODES_N)
    # charlie = Client('Charlie', NODES_N)

    # Alice and Bob write concurrently and sync

    alice.write_add(zero, 'a')
    bob.write_add(one, 'b')
    zero.sync(one)

    # Alice writes add and syncs, causal

    alice.write_add(zero, 'x')
    zero.sync(one)

    # Bob writes remove and syncs, causal

    bob.write_remove(one, 'x')
    zero.sync(one)

    # Alice adds and Bob adds-removes, concurrent add wins

    alice.write_add(zero, 'x')
    bob.write_add(one, 'x')
    bob.write_remove(one, 'x')
    zero.sync(one)

    # Alice adds and Bob removes separate element, concurrent without conflict

    alice.write_add(zero, 'aa')
    bob.write_remove(one, 'b')
    zero.sync(one)

    # Alice and Bob both remove the same element, concurrent without conflict

    alice.write_remove(zero, 'aa')
    alice.write_add(zero, 'aa')
    alice.write_remove(zero, 'aa')
    bob.write_remove(one, 'aa')
    zero.sync(one)


    # alice.write_add(zero, 'aa')
    # bob.write_add(one, 'bb')
    # alice.write_remove(zero, 'aa')

    # zero.sync(one)
    
    # charlie.write_add(two, 'cc')

    # zero.sync(two)

    # alice.write_add(zero, 'x')
    # alice.write_remove(zero, 'x')
    # charlie.write_add(two, 'x')

    # zero.sync(two)



if __name__ == '__main__':
    simulate()
