import requests 
import sys
from Naked.toolshed.shell import muterun_js,execute_js
import re
import json

"""

    spindex = Index(bbox=(0, 0, 100, 100))
    spindex.insert(item, item.bbox)
    overlapbbox = (51, 51, 86, 86)
    matches = spindex.intersect(overlapbbox)

"""

__version__ = "0.25.0"

#PYTHON VERSION CHECK
import sys
import hashlib
PYTHON3 = int(sys.version[0]) == 3
if PYTHON3:
    xrange = range


def _normalize_rect(rect):
    x1, y1, x2, y2 = rect
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return (x1, y1, x2, y2)


def _loopallchildren(parent):
    for child in parent.children:
        if child.children:
            for subchild in _loopallchildren(child):
                yield subchild
        yield child


def printall(self):
    for node in self.nodes:
        print node.item
        print node.rect
        print node.hash
        print "\n"

        for child in self.children:
            printall(child)


def printallhash(self):
    for node in self.nodes:
        print node.hash

        for child in self.children:
            printallhash(child)


class _QuadNode(object):    
    def __init__(self, item, rect,parent):
        self.item = item
        self.rect = rect
        self.hash=''
        self.parent=parent

    def recompute_hash(self):
        self.hash=hashlib.sha224(str(self.rect)).hexdigest()
        print "Computing hash of Node"


    def hashcal(self):
        self.recompute_hash()

    def printall(self):
        print node.item
        print node.rect
        print "\n"




class _QuadTree(object):
    """
    Internal backend version of the index.
    The index being used behind the scenes. Has all the same methods as the user
    index, but requires more technical arguments when initiating it than the
    user-friendly version.
    """
    
    def __init__(self, x, y, width, height, max_items, max_depth,parent, _depth=0):
        self.nodes = []
        self.children = []
        self.center = (x, y)
        self.width, self.height = width, height
        self.max_items = max_items
        self.max_depth = max_depth
        self._depth = _depth
        self.hash=""
        self.parent=parent

        
    def __iter__(self):
        for child in _loopallchildren(self):
            yield child

    def hashcal(self):
        for child in self.children:
            if child.children:
                child.hashcal()


            if child.nodes:
                for n in child.nodes:
                    n.recompute_hash()

                child.recompute_hash()
            child.recompute_hash()
            self.recompute_hash()

        for n in self.nodes:

            n.recompute_hash()

    def printall(self):
        for node in self.nodes:
            print(node.item)
            print(node.rect)
            print(node.hash)
            print("\n")

        for child in self.children:

            if child.children:
                child.printall()


            
    def _insert(self, item, bbox):
        rect = _normalize_rect(bbox)
        if len(self.children) == 0:
            node = _QuadNode(item, rect,self)
            self.nodes.append(node)
            print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
            print("Appended the QuadNode to the tree --Line 141")
            print rect
            print item
            print "\n"

            
            if len(self.nodes) > self.max_items and self._depth < self.max_depth:
                self._split()
                print("Here the nodes were split")
        else:
            print "Now inserting into children"
            self._insert_into_children(item, rect)
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                     
   


    def _intersect(self, rect, results=None):
        if results is None:
            rect = _normalize_rect(rect)
            results = set()
        # search children
        if self.children:
            if rect[0] <= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[0]._intersect(rect, results)
                if rect[3] >= self.center[1]:
                    self.children[1]._intersect(rect, results)
            if rect[2] >= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[2]._intersect(rect, results)
                if rect[3] >= self.center[1]:
                    self.children[3]._intersect(rect, results)
        # search node at this level
        for node in self.nodes:
            if (node.rect[2] >= rect[0] and node.rect[0] <= rect[2] and 
                node.rect[3] >= rect[1] and node.rect[1] <= rect[3]):
                results.add(node.item)
        return results


    def _delete(self, rect, results=None):
        if results is None:
            rect = _normalize_rect(rect)
            results = set()
        # search children
        if self.children:
            if rect[0] <= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[0]._delete(rect, results)
                if rect[3] >= self.center[1]:
                    self.children[1]._delete(rect, results)
            if rect[2] >= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[2]._delete(rect, results)
                if rect[3] >= self.center[1]:
                    self.children[3]._delete(rect, results)
        # search node at this level
        for node in self.nodes:
            if (node.rect[0] == rect[0] and node.rect[1] == rect[1] and node.rect[2] == rect[2] and node.rect[3] == rect[3]):
                print ("deleting"+str(node.item))
                self.nodes.remove(node)


    def _transfer(self,rect,newowner):
        rect=_normalize_rect(rect)

        if self.children:
            if rect[0] <= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[0]._transfer(rect, newowner)
                if rect[3] >= self.center[1]:
                    self.children[1]._transfer(rect, newowner)
            if rect[2] >= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[2]._transfer(rect, newowner)
                if rect[3] >= self.center[1]:
                    self.children[3]._transfer(rect, newowner)

        for node in self.nodes:
            if (node.rect[0] == rect[0] and node.rect[1] == rect[1] and 
                node.rect[2] == rect[2] and node.rect[3] == rect[3]):

                node.item=newowner






    def _insert_into_children(self, item, rect):
        # if rect spans center then insert here
        if (rect[0] <= self.center[0] and rect[2] >= self.center[0] and
            rect[1] <= self.center[1] and rect[3] >= self.center[1]):
            node = _QuadNode(item, rect,self)
            print " Start of --------------------------------------------------------------"
            print "This is insertintocildren and here the QuadNode is being appended to it"
            self.nodes.append(node)
        else:
            # try to insert into children
            if rect[0] <= self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[0]._insert(item, rect)
                    print ("executed insertintochildren and added to the first if")
                    print item
                    print rect
                if rect[3] >= self.center[1]:
                    self.children[1]._insert(item, rect)
                    print ("executed insertintochildren and added to the second if")
                    print item
                    print rect

            if rect[2] > self.center[0]:
                if rect[1] <= self.center[1]:
                    self.children[2]._insert(item, rect)
                    print ("executed insertintochildren and added to the third if" )
                    print item
                    print rect

                if rect[3] >= self.center[1]:
                    self.children[3]._insert(item, rect)
                    print ("print executed insertintochildren and added to the third if")
                    print item
                    print rect
        print "---------------------------------------End of insertintochildren-----------------------"
        

                    
    def _split(self):
        print "Split starts {{{{{{{{{{{{{{{{{{{{{{{{{{{"
        quartwidth = self.width / 4.0
        quartheight = self.height / 4.0
        halfwidth = self.width / 2.0
        halfheight = self.height / 2.0
        x1 = self.center[0] - quartwidth
        x2 = self.center[0] + quartwidth
        y1 = self.center[1] - quartheight
        y2 = self.center[1] + quartheight
        new_depth = self._depth + 1
        self.children = [_QuadTree(x1, y1, halfwidth, halfheight,
                                   self.max_items, self.max_depth, self,new_depth),
                         _QuadTree(x1, y2, halfwidth, halfheight,
                                   self.max_items, self.max_depth, self,new_depth),
                         _QuadTree(x2, y1, halfwidth, halfheight,
                                   self.max_items, self.max_depth, self,new_depth),
                         _QuadTree(x2, y2, halfwidth, halfheight,
                                   self.max_items, self.max_depth, self,new_depth)]
        nodes = self.nodes
        print "The actual splitting operation"
        self.nodes = []
        for node in nodes:
            print("Here insert_into_children under split is called on ")
            print node.item
            print node.rect
            self._insert_into_children(node.item, node.rect)
        print "Split ends }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}"

    def __len__(self):
        """
        Returns:
        
        - A count of the total number of members/items/nodes inserted
        into this quadtree and all of its child trees.
        """
        size = 0
        for child in self.children:
            size += len(child)
        size += len(self.nodes)
        return size

    def recompute_hash(self):
        print "Computinghash"
        print (type(self))
        child_hashes=""
        node_hashes=""
        individualnodehash=""
        for child in self.children:
            child_hashes+=child.hash
        for nodes in self.nodes:
            node_hashes+=nodes.hash
        individualnodehash

        nethash=child_hashes+node_hashes+str(self.center)

        if isinstance(self,_QuadNode):
            self.hash=hashlib.sha224(str(self.rect)).hexdigest()
        else:
            self.hash=hashlib.sha224(nethash).hexdigest()


MAX_ITEMS = 10
MAX_DEPTH = 20


class Index(_QuadTree):
    """
    The top spatial index to be created by the user. Once created it can be
    populated with geographically placed members that can later be tested for
    intersection with a user inputted geographic bounding box. Note that the
    index can be iterated through in a for-statement, which loops through all
    all the quad instances and lets you access their properties.
    
    Example usage:
    
    >>> spindex = Index(bbox=(0, 0, 100, 100))
    >>> spindex.insert('duck', (50, 30, 53, 60))
    >>> spindex.insert('cookie', (10, 20, 15, 25))
    >>> spindex.insert('python', (40, 50, 95, 90))
    >>> results = spindex.intersect((51, 51, 86, 86))
    >>> sorted(results)
    ['duck', 'python']
    """
    
    def __init__(self, bbox=None, x=None, y=None, width=None, height=None, max_items=MAX_ITEMS, max_depth=MAX_DEPTH):
        """
        Initiate by specifying either 1) a bbox to keep track of, or 2) with an xy centerpoint and a width and height.
        
        Parameters:
        - **bbox**: The coordinate system bounding box of the area that the quadtree should
            keep track of, as a 4-length sequence (xmin,ymin,xmax,ymax)
        - **x**:
            The x center coordinate of the area that the quadtree should keep track of. 
        - **y**
            The y center coordinate of the area that the quadtree should keep track of.
        - **width**:
            How far from the xcenter that the quadtree should look when keeping track. 
        - **height**:
            How far from the ycenter that the quadtree should look when keeping track
        - **max_items** (optional): The maximum number of items allowed per quad before splitting
            up into four new subquads. Default is 10. 
        - **max_depth** (optional): The maximum levels of nested subquads, after which no more splitting
            occurs and the bottommost quad nodes may grow indefinately. Default is 20. 
        """
        if bbox:
            x1, y1, x2, y2 = bbox
            width, height = abs(x2-x1), abs(y2-y1)
            midx, midy = x1+width/2.0, y1+height/2.0
            super(Index, self).__init__(midx, midy, width, height, max_items, max_depth,None,2)

        elif all(x, y, width, height):
            super(Index, self).__init__(x, y, width, height, max_items, max_depth,None)

        else:
            raise Exception("Either the bbox argument must be set, or the x, y, width, and height arguments must be set")

    def insert(self, item, bbox):
        """
        Inserts an item into the quadtree along with its bounding box.
        
        Parameters:
        - **item**: The item to insert into the index, which will be returned by the intersection method
        - **bbox**: The spatial bounding box tuple of the item, with four members (xmin,ymin,xmax,ymax)
        """
        self._insert(item, bbox)

    def delete(self,bbox):
        return self._delete(bbox)

######THIS IS THE ABSOLOUTE MAIN FUNCTION############
    def insertblock(self,item,bbox):

        dim=str(bbox).strip("()")
        dim= dim.replace(',', '')
        dim=str(dim)
        result=self.intersect(bbox)
        if not self.hash:
            self.hash='0'
        if not result:
            a=[str(self.hash),str(dim),str(item)]
            b=":".join(a)
            b=str(b)
            print(type(b))
            print b
            b=b.replace(' ','-')
            response=muterun_js("transaction.js",b)
            test1=re.match("AssetID(.*)AssetEND",response.stdout)
            Obtained_Asset_ID=test1.group(1)
            self.insert(Obtained_Asset_ID,bbox)
            print ("Property Sucessfully inserted"+str(dim))
            self.hashcal()
        else:
            print ("There is an intersection with")
            print ([i for i in result])


#######ALWAYS CALL THIS ##############
    def intersect(self, bbox):
        """
        Intersects an input boundingbox rectangle with all of the items
        contained in the quadtree.
        
        Parameters:
        - **bbox**: A spatial bounding box tuple with four members (xmin,ymin,xmax,ymax)
        
        Returns:
        - A list of inserted items whose bounding boxes intersect with the input bbox.
        """
        return self._intersect(bbox)

    def transfer(self,bbox,newowner):
        self._transfer(bbox,newowner)

def main():
    spindex=Index(bbox=(0,0,1000,1000))
    spindex.hash="000"
    print "enter property name "
    propertyname=str(raw_input())
    print "Enter property dimensions in tuple format"
    unformedinput=raw_input()
    dimensions=tuple(int(x.strip()) for x in unformedinput.split(','))
    result=spindex.intersect(dimensions)
    if not result:
        a=[str(spindex.hash),str(unformedinput),str(propertyname)]
        b=":".join(a)
        b=str(b)
        print(type(b))
        response=muterun_js("transaction.js",b)
        #print response.stdout
        spindex.insert(response.stdout,dimensions)
        print ("Property Sucessfully inserted"+str(dimensions)+propertyname)
        spindex.hashcal()
    else:
        print ("There is an intersection with")
        print ([i for i in result])

def test():
    sp=Index(bbox=(0,0,20,20))
    for i in range(20):
        sp.insert(i,(i,i,i+1,i+1))

##THIS IS A TEST INSERTION FUNCTION
def insertontoblockchain(what):
    issueurl= 'http://testnet.api.coloredcoins.org:80/v3/issue'
    funded_address='moXvpRmNQXkfpggXmQGvE3gbp3QyM9cpdq'
    metadata= {
        'assetId': '2',
        'assetName': 'Dishant',
        'issuer': 'Genius',
        'description': '0,0,5,5 Hash 20fd37c942f0f95b0a2215f336ba298438f3a0a5b11e6ae9c4f71ecb'}

    metadata1=json.dumps(metadata)
    asset = {
    'issueAddress': 'moXvpRmNQXkfpggXmQGvE3gbp3QyM9cpdq',
    'amount': 1,
    'divisibility': 0,
    'fee': 5000,
    'reissueable':'false',
    'metadata' : a}
    r=requests.post(issueurl,data=asset)
    reply=r.json()
    print(reply)
    """issuehash=reply['txHex']
    print(issuehash)"""


##THIS IS A TEST SIGNING FUNCTION
def signatransaction(inputstuff):
    response=muterun_js("sign_transaction.js",inputstuff)
    regex=r"\[(.*?)\]"
    matchobj=re.search(regex,response.stdout)
    print (matchobj.group(1))


def broadcast(hexdata):
    broadcasturl= 'http://testnet.api.coloredcoins.org:80/v3/broadcast'
    r=requests.post(broadcasturl,data={'txHex':hexdata})
    response=r.json()
    print response


"""THIS IS THE MAIN INSERT FUNCTION"""
def completeinsert():
    issueurl= 'http://testnet.api.coloredcoins.org:80/v3/issue'
    funded_address='moXvpRmNQXkfpggXmQGvE3gbp3QyM9cpdq'

    assetin= {
    'issueAddress': 'moXvpRmNQXkfpggXmQGvE3gbp3QyM9cpdq',
    'amount': 1,
    'divisibility': 0,
    'fee': 5000,
    'reissueable':'false',
    'metadata.assetName': 'Dishant',
    'metadata.issuer': 'Genius',
    'metadata.description': '0,0,5,5 Hash 20fd37c942f0f95b0a2215f336ba298438f3a0a5b11e6ae9c4f71ecb'
    }

    r=requests.post(issueurl,data=assetin)
    reply=r.json()
    issuehash=reply['txHex']
    asset=reply['assetId']

    response=muterun_js("sign_transaction.js",issuehash)
    regex=r"\[(.*?)\]"
    matchobj=re.search(regex,response.stdout)
    broadcast(matchobj.group(1))
    print(asset)

def insertthroughnodejs(a):
    print("Going through the insertion function")
    response=muterun_js("transaction.js",a)
    print (response.stdout)
    test1=re.match("AssetID(.*)AssetEND",response.stdout)
    print test1.group(1)
    Obtained_Asset_ID=test.group(1)
    #test2=re.match("AssetID(.*)AssetEND",response.stdout)

    #regex=r"\[(.*?)\]"
    #matchobj=re.search(regex,response.stdout)
    #print (matchobj.group(1))



if __name__ == "__main__":
    main()

