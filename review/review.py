#!/bin/env python3
import os, sys

ROWSEP = '\n'
COLSEP = '\t'
ENTITIES_PER_ROW = 4

BOLDSEP = '!'
REPLSEP = '@'

SEVERITY = {
	'm' : 'minor',
	'a' : 'average',
	'c' : 'critical',
}

TEX_BOLD_CMD = 'genbf'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def parseCtxStr(data):
	v = data.split(BOLDSEP)
	if (len(v) % 2 == 0):
		eprint("Parse error[ ctx]: '{0}'".format(data))
		return [data], {}
	if (len(v) == 0):
		return [data], {}

	replacements = {}
	output = []
	for i, item in enumerate(v):
		if (i % 2 == 1):
			ss = item.split('@')
			if (len(ss) != 2):
				eprint("Parse error[ ctx]: '{0}'".format(item))
				return replacements
			replacements.update({ss[0]: ss[1]})
			output += [ss[0]]
		else:
			output += [item]
	return output, replacements


def parseLine(line):
	v = line.split(COLSEP)
	if (len(v) < ENTITIES_PER_ROW):
		eprint("Parse error[line]: '{0}'".format(line))
		return -1, [], {}, "", ""

	page = int(v[0])

	ctxStr = v[1]
	parsed, rep = parseCtxStr(ctxStr)

	rsn = v[2]

	sevc = v[3]
	sev = SEVERITY[sevc]

	return page, [parsed, rep, rsn, sev]

def toTex(byPage):
	hline = "\\hline" + ROWSEP
	cline = "\\cline{2-5}"
	multirow_fmt = "{page:10}"#"\\multirow{{{count}}}{{*}}{{{page}}}"
	data_fmt = "&".join(["{page:10}", "{context:100}", "{suggestion:40}", "{reason:20}", "{severity:20}"]) + '\\\\{ate}' + ROWSEP

	out_str = ''
	out_str += hline
	out_str += data_fmt.format(page="Page \\#", context="Context", suggestion="Suggestion", reason="Reason", severity="Severity", ate="")
	
	for page, vdata in byPage.items():
		mr_page = multirow_fmt.format(count=len(vdata), page=page)
		data_str = hline
		for i, data in enumerate(vdata):
			ctx, rep, rsn, sev = data
			ctx_str = ''.join(map(lambda k: k if k not in rep else "\\{0}{{{1}}}".format(TEX_BOLD_CMD, k), ctx))
			sug_str = ', '.join(rep.values())
			data_str += data_fmt.format(page = mr_page if i == 0 else "", context = ctx_str, suggestion = sug_str, reason = rsn, severity = sev, ate = cline)
		out_str += data_str
	out_str += hline
	return out_str

def toTexTable(contents, align_string):
	out_str = "\\begin{{longtabu}} to \\textwidth {{{0}}}".format(align_string) + ROWSEP;
	out_str += contents
	out_str += "\\end{longtabu}"
	return out_str


def main():
	fInput = sys.argv[1]

	byPage = {}
	with open(fInput, 'r') as f:
		for line in f:
			if (len(line[:-1]) == 0):
				continue

			#print(line)
			#print(parseLine(line[:-1]))
			page, data = parseLine(line[:-1])
			if (page not in byPage):
				byPage[page] = []
			byPage[page] += [data]

	contents = toTex(byPage)
	res = toTexTable(contents, "|r|p{40mm}|X|X|c|")
	print(res)


if __name__ == '__main__':
	if (len(sys.argv) < 2):
		eprint("Usage: {0} file".format(sys.argv[0]))
		exit(0)
	main()