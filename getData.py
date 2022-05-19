import requests
import vcfpy
import argparse
import io
import random
from datetime import datetime

BASE_URL = 'https://divbrowse.ipk-gatersleben.de/shape/brapi/v2/variantmatrix'

VARIANTSET_URL = 'https://private-anon-dbb1c053eb-brapigenotyping20.apiary-mock.com/brapi/v2/variantsets/'
REFSET_URL = 'https://private-anon-dbb1c053eb-brapigenotyping20.apiary-mock.com/brapi/v2/referencesets/'
VARIANT_URL = 'https://private-anon-dbb1c053eb-brapigenotyping20.apiary-mock.com/brapi/v2/variants/'
REFERENCE_URL = 'https://private-anon-dbb1c053eb-brapigenotyping20.apiary-mock.com/brapi/v2/references/'

parser = argparse.ArgumentParser()
parser.add_argument('--divbrowse', help='Use divbrowse endpoint', action="store_true")
parser.add_argument('-i', '--endpoint', default=BASE_URL, help='endpoint to call against')
parser.add_argument('-o', '--output', default='/dev/stdout', help='Must end with .gz')
parser.add_argument('--dimensionVariantPage')
parser.add_argument('--dimensionVariantPageSize')
parser.add_argument('--dimensionCallSetPage')
parser.add_argument('--dimensionCallSetPageSize')
parser.add_argument('--positionRange')
parser.add_argument('--germplasmDbId')
parser.add_argument('--germplasmName')
parser.add_argument('--germplasmPUI')
parser.add_argument('--callSetDbId')
parser.add_argument('--variantDbId')
parser.add_argument('--variantSetDbId')
parser.add_argument('--expandHomozygotes')
parser.add_argument('--unknownString')
parser.add_argument('--sepPhased')
parser.add_argument('--sepUnphased')
args = parser.parse_args()


def buildURL():
    if args.divbrowse:
        return 'https://divbrowse.ipk-gatersleben.de/shape/brapi/v2/variantmatrix?positionRanges=1:551-1000&germplasmDbIds=BRIDGE_WGS_HOR_2237,BRIDGE_WGS_HOR_3460'
    url = args.endpoint + '/variantmatrix'
    first = True
    if not args.dimensionVariantPage is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'dimensionVariantPage=' + args.dimensionVariantPage
    if not args.dimensionVariantPageSize is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'dimensionVariantPageSize=' + args.dimensionVariantPageSize
    if not args.dimensionCallSetPage is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'dimensionVariantCallSetPage=' + args.dimensionCallSetPage
    if not args.dimensionCallSetPageSize is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'dimensionCallSetPageSize=' + args.dimensionCallSetPageSize
    if not args.positionRange is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'positionRange=' + args.positionRange
    if not args.germplasmDbId is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'germplasmDbId=' + args.germplasmDbId
    if not args.germplasmName is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'germplasmName=' + args.germplasmName
    if not args.germplasmPUI is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'germplasmPUI=' + args.germplasmPUI
    if not args.callSetDbId is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'callSetDbId=' + args.callSetDbId
    if not args.variantSetDbId is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'variantSetDbId=' + args.variantSetDbId
    if not args.expandHomozygotes is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'expandHomozygotes=' + args.expandHomozygotes
    if not args.unknownString is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'unknwonString=' + args.unknownString
    if not args.sepPhased is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'sepPhased=' + args.sepPhased
    if not args.sepUnphased is None:
        if first:
            url += '?'
        else:
            url += '&'
        first = False
        url += 'sepUnphased=' + args.sepUnphased
    return url


def getVariantMatrix():
    url = buildURL()
    params = {'page': 0, 'pageSize': 10}
    print(url)
    res = requests.get(url, params)
    data = res.json()

    return data


def getVariantSet(variantSetDbId):
    url = VARIANTSET_URL + variantSetDbId
    print(url)
    params = {'page': 0, 'pageSize': 10}
    if args.divbrowse:
        res = requests.get(url)
    else:
        res = requests.get(url, params)
    return res.json()


def getReferenceSet(referenceSetDbId):
    url = REFSET_URL + referenceSetDbId
    print(url)
    params = {'params': 0, 'pageSize': 10}
    res = requests.get(url, params)
    return res.json()


def getVariant(variantDbId):
    url = VARIANT_URL + variantDbId
    print(url)
    params = {'params': 0, 'pageSize': 10}
    res = requests.get(url, params)
    return res.json()


def getReference(referenceDbID):
    return None


def writeVCFHeader(res):
    callsets = res['callSetDbIds']
    genotypeFields = res['genotypeFields']
    variantsets = res['variantSetDbIds']
    variants = res['variants']

    variantsetid = variantsets[0]
    if not args.variantSetDbId is None:
        variantsetid = args.variantSetDbId
    variantset = getVariantSet(variantsetid)

    reference = getReferenceSet(variantset['result']['referenceSetDbId'])

    header = vcfpy.Header(samples=vcfpy.SamplesInfos(callsets))

    header.add_line(vcfpy.HeaderLine('fileformat', 'VCFv4.3'))
    header.add_line(vcfpy.HeaderLine('fileDate', datetime.today().strftime('%Y%m%d')))
    header.add_line(vcfpy.HeaderLine('source', buildURL()));
    header.add_line(vcfpy.HeaderLine('reference', reference['result']['assemblyPUI']))

    contigs = []
    for variant in variants:
        v = getVariant(variant['variantDbId'])
        if not variant['contig'] in contigs:
            contigs.append(variant['contig'])
    for c in contigs:
        header.add_contig_line(vcfpy.OrderedDict([('ID', c), ('length', 0)]))

    header.add_format_line(
        vcfpy.OrderedDict([('ID', 'GT'), ('Number', 1), ('Type', 'String'), ('Description', 'Genotype')]))
    for genotypeField in genotypeFields:
        header.add_format_line(vcfpy.OrderedDict(
            [('ID', genotypeField['fieldAbbreviation']), ('Number', 1), ('Type', genotypeField['fieldType']),
             ('Description', genotypeField['fieldName'])]))
    return header


def nucGenerator(i):
    if i == 0:
        return 'A'
    if i == 1:
        return 'C'
    if i == 2:
        return 'G'
    if i == 3:
        return 'T'


response = getVariantMatrix()
header = writeVCFHeader(response['result'])

stream = open(args.output, 'wb')
with vcfpy.Writer.from_stream(stream, header, path=args.output, use_bgzf=True) as writer:
    ft = ["GT"]
    for field in response['result']['genotypeFields']:
        ft.append(field['fieldAbbreviation'])
    data = [*zip(*response['result']['data'])]
    for i in range(0, len(data)):
        calls = []
        for j in range(0, len(data[i])):
            sample = response['result']['callSetDbIds'][j]
            tmp = []
            for genotypeField in response['result']['genotypeFields']:
                tmp.append((genotypeField['fieldAbbreviation'], genotypeField['fieldMatrix'][j][i]))
            tmp.append(('GT', data[i][j]))
            calls.append(vcfpy.Call(sample, vcfpy.OrderedDict(tmp)))
        alt = nucGenerator(random.randint(0, 3))
        ref = nucGenerator(random.randint(0, 3))
        while ref == alt:
            ref = nucGenerator(random.randint(0, 3))
        record = vcfpy.Record(CHROM=response['result']['variants'][i]['contig'],
                              POS=response['result']['variants'][i]['start'],
                              ID=[response['result']['variants'][i]['variantDbId']], REF=ref,
                              ALT=[vcfpy.Substitution(type_="SNV", value=str(alt))], QUAL=None, FILTER=["PASS"],
                              INFO={}, FORMAT=ft, calls=calls)
        writer.write_record(record)
print('')
print('Finished. Results were written to ' + args.output)
