__author__ = 'soumadipmukherjee'
import random
import numpy
import math


def readFastq(filename, filename2):
    """
    Parse read and quality strings from a FASTQ file with sequencing reads.
    @author: Ben Langmead & Jacob Pritt.
    Input: file path
    Output: A list of reads, the list of qualities
    """
    #sequence will be an array of read objects
    #the object will have the ID, the original sequence, and the reverse complement
    sequences = []
    compMapping = {
        'A' : 'T',
        'a' : 'T',
        'T' : 'A',
        't' : 'A',
        'C' : 'G',
        'c' : 'G',
        'G' : 'C',
        'g' : 'C',
        'N' :'N',
        'n': 'N'
    }
    fh = filename
    fh2 = filename2
    #with open(filename) as fh:
    #    with open(filename2) as fh2:
    while True:
        read_obj = {
            "id": None,
            #"seq": None,
            #"rev_comp_seq": None
            "mate1":None,
            "mate2":None
        }
        #Do all of the reading here. READ FOUR lines for each READ
        id = fh.readline().rsplit() #read the id
        id_2= fh2.readline().rsplit()
        seq = fh.readline().rstrip() #read base sequence
        seq_2 = fh2.readline().rstrip()
        fh.readline() # skip placeholder line
        fh.readline() # base quality line
        fh2.readline()
        fh2.readline()
        #End of Reading here

        if len(seq) == 0 or len(seq_2)== 0:
            break
        #Make the mates upper case
        seq = seq.upper()
        seq_2 = seq_2.upper()

        #Store the mate ids in the structure to retun
        read_obj["mate1_id"] = id[0] # skip name line
        read_obj["mate2_id"] = id_2[0]

        #produce the id of the Reads by removing the las part
        end =read_obj["mate1_id"].rindex(':')#get the last index of the colon
        read_obj["id"] = read_obj["mate1_id"][:end]

        #store the length of mate1 so we do kmer has over the bridge of mate1 and mate2
        read_obj["mate1_len"] = len(seq)


        #construct Read1
        #Reverse complement mate2 and concatenat it to mate1
        reverse_2 = seq_2[::-1]
        reverse_comp_r2=""
        for x in range(0, len(reverse_2)):
            try:
                reverse_comp_r2 += compMapping[reverse_2[x]]
            except KeyError as e:
                #print e
                continue
        mate1 = seq + reverse_comp_r2

        read_obj["read1"] = mate1


        #construct Read2
        #Reverse complement mate1 and concatenate it with mate2
        reverse_1 = seq[::-1]
        reverse_comp_r1= ""
        for x in range(0, len(reverse_1)):
            try:
                reverse_comp_r1 += compMapping[reverse_1[x]]
            except KeyError as e:
                #print e
                continue

        mate2 = reverse_comp_r1 + seq_2

        read_obj["read2"] = mate2
        sequences.append(read_obj)
    return sequences
def buildKmerListForReads(reads, k_length):
    for r_obj in reads:
        r1 = r_obj["read1"]
        r2 = r_obj["read2"]
        bridgeIndex = r_obj["mate1_len"] - 1
        kmer_array =  []
        #go from 0 to bridgeIndex
        #Dont consider Kmers with 'N' base in them
        for x in range(0,((bridgeIndex+1)-k_length)):
            k1 = r1[x:x+k_length]
            k2 = r2[x:x+k_length]
            b1 = 'N' in k1
            b2 = 'N' in k2
            if b1 == True and b2 == True:
                continue
            elif b1 == True and b2 == False:
                kmer_array.append(k2)
            elif b1 == False and b2 == True:
                kmer_array.append(k1)
            elif b1 <= b2:
                kmer_array.append(k1)
            else:
                kmer_array.append(k2)
        #from bridge index to the end of the read
        for x in range(bridgeIndex,((len(r1))-k_length)):
            k1 = r1[x:x+k_length]
            k2 = r2[x:x+k_length]
            b1 = 'N' in k1
            b2 = 'N' in k2
            if b1 == True and b2 == True:
                continue
            elif b1 == True and b2 == False:
                kmer_array.append(k2)
            elif b1 == False and b2 == True:
                kmer_array.append(k1)
            elif b1 <= b2:
                kmer_array.append(k1)
            else:
                kmer_array.append(k2)
        r_obj["kmer_list"] = kmer_array
    return


#transform the list of kmers to vectors representations
def translateKmerList(reads):
    for r_obj in reads:
        kmer_list = r_obj["kmer_list"]
        kmer_vectors = []
        for k in kmer_list:
                kmer_vectors.append(translateKmer(k))

        r_obj["kmer_vectors"] = kmer_vectors
    return


#function returns the vector representation of the kmer, according to our mapping
def translateKmer(kmer):
    translate_table = {
        'A': 1,
        'T': -1,
        'C': 2,
        'G': -2
    }
    vector = []
    for k in kmer:
        vector.append(translate_table[k])
    return vector

#function will generate N random kmers of length k_length and return the random elements
#in and array
def generateNRandomVectors(n, k_length):
    random_vectors = []
    mapping= {
        1: 1, #A
        2: -1, #T
        3: 2, #C
        4: -2 #G
    }
    listOfOptions = [1, -1, 2, -2]
    for x in range(0, n):
        r_vec = []
        for y in range(0,k_length):
            r_vec.append(random.choice(listOfOptions))

        random_vectors.append(r_vec)
    return random_vectors

def produceRandomMatrix(randomVectors, k_length):
    randomVectorsMatrix = numpy.zeros((len(randomVectors), k_length), dtype= numpy.int8)
    i = 0;
    j = 0;
    for r in randomVectors:
        for val in r:
            randomVectorsMatrix[i][j] = val
            j+=1

        j = 0
        i +=1
    return randomVectorsMatrix

def produceKmerMatrix(kmers, k_length):
    kmerMatrix = numpy.zeros((len(kmers), k_length), dtype=numpy.int8)
    i = 0
    j = 0
    for kmer in kmers:
        for val in kmer:
            kmerMatrix[i][j] = val
            j+= 1
        i+=1
        j=0

    kmerMatrix = kmerMatrix.transpose()
    # for val in kmers:
    #     kmerMatrix[i][j] = val
    #     j+=1

    return kmerMatrix



def produceAbundanceMatrix(reads, k_length, h_size):
    randomVectorMatrix = produceRandomMatrix(generateNRandomVectors(h_size, k_length), k_length )
    abundanceMatrix = numpy.zeros((len(reads),2**h_size), dtype=numpy.int32)
    #print randomVectorMatrix
    #print randomVectorMatrix.shape
    bitVector = []
    l_i = []
    g_j = []
    MAX_CONSTANT_32 = 4294967295.0
    read_index = 0
    for r_obj in reads:
        print "Reading another one...", str(read_index)
        kmers = r_obj["kmer_vectors"]
        kmerMatrix = produceKmerMatrix(kmers, k_length)
        #print kmerMatrix
        #print kmerMatrix.shape
        #RMatrix = numpy.dot(randomVectorMatrix , kmerMatrix)
        RMatrix = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*kmerMatrix)] for X_row in randomVectorMatrix]
        #print RMatrix
        # shape  = RMatrix.shape
        #print shape
        for x in range(0, len(RMatrix[0])):
            col = [i[x] for i in RMatrix]
            #print col
            normalized = math.sqrt(sum([y ** 2  for y in col]))
            #print normalized
            cosine = [y/normalized for y in col]
            # print cosine
            #print "Normalized", str(normalized)
            #print cosine
            newCol = []
            for c in cosine:
                if c < -1 or c>1:
                    print "error"
                theta = numpy.arccos(c)
                # print theta
                if theta < (math.pi/2):
                    newCol.append(1)
                else:
                    newCol.append(0)
            bitVector.append(newCol)
        readIndices = []
        for vec in bitVector:
            str_rep = ""
            for i in vec:
                str_rep += str(i)
            readIndices.append(int(str_rep, 2))


        #print readIndices
        for index in readIndices:
            abundanceMatrix[read_index][index] += 1

        read_index+=1
    print "Done Reading DAMM FILES"
    #file = open('avi.txt', 'w')
    for i in range(0, len(reads)):
        j = 0
        print "Doing Read: ", str(i)
        while j < (2**h_size):
            if abundanceMatrix[i][j] != 0:
                print abundanceMatrix[i][j]
                print i, j
                print "#"*3
            if( j %100 == 0):
                print "Column: ", str(j)
            j +=1

    # file.write(str(abundanceMatrix))
    # file.close()

    # print abundanceMatrix[0][0]
    # for i in range (0, len(reads)):
    #     for j in range(0, 2**h_size):
    #         print str(i), str(j)
    #         #print abundanceMatrix[i][j]
    #     print
    #     print
    # print "DONE"
    # for i in range(0,len(reads)):
    #     r_hits = []
    #     for j in range(0,2**h_size):
    #         if abundanceMatrix[i][j] != 0:
    #             r_hits.append(abundanceMatrix[i][j])
    #     #print sum(c_hits)
    #     l_i.append(math.sqrt(sum(r_hits))/(2**h_size))
    #
    #print l_i
    # print "DONE1"
    # for j in range(0,2**h_size):
    #     col_hit_count = 0
    #     for i in range(0,len(reads)):
    #         if abundanceMatrix[i][j] != 0:
    #             col_hit_count+=1
    #     if col_hit_count == 0:
    #         g_j.append(MAX_CONSTANT_32)
    #     else:
    #         g_j.append(math.log((len(reads)/col_hit_count),2))
    #         #print
    # #print g_j
    # print "DONE2"
    # #print l_i
    # for i in range(0, len(reads)):
    #     for j in range(0, 2**h_size):
    #         #print abundanceMatrix[i][j], g_j[j], l_i[i]
    #         if(abundanceMatrix[i][j] > 100):
    #             print "HERE"
    #             print g_j[j], l_i[i]
    #         abundanceMatrix[i][j]*= (g_j[j]/l_i[i])
    #
    # #print abundanceMatrix[0][readIndices[len(readIndices) -1]]
    # print "DONE3"
    #for i in range (0, len(reads)):
    #     for j in range(0, 2**h_size):
    #         print abundanceMatrix[i][j],
    #     print
    # return


def prettyPrintObject(sequences):
    for x in sequences:
        print "#" * 100
        print "ID: ", x["id"]
        print "ID1: ", x["mate1_id"]
        print "ID2: ", x["mate2_id"]
        print "Read1: ", x["read1"]
        print "Read2: ", x["read2"]
        print "Mate1 Length: ", x["mate1_len"]
        # print "S : ", x["seq"]
        # print "RC: ", x["rev_comp_seq"]
        print "#" * 100
        print ""

#prettyPrintObject(readFastq("dummyTest.fastq"))

#rettyPrintObject(readFastq("r1_short.fq", "r2_short.fq"))

# r = readFastq("r1_short.fq", "r2_short.fq")
# print "Finished reading files"
# #print r
# # prettyPrintObject(r)
# buildKmerListForReads(r, 33)
# print "Finished building kmwe List for each read"
#
# # #print r
# #
# translateKmerList(r)
# print "Finished Translating kmer list"
# # print r
#
# #randomVecs = generateNRandomVectors(10, 4)
#
# #produceRandomMatrix(randomVecs, 4)
# produceAbundanceMatrix(r, 33, 29)


#print translateKmer("ATCG")