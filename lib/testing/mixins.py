class AssertsMixin(object):

    def assertItemsEqual(self, items1, items2):
        return set(items1) == set(items2)
