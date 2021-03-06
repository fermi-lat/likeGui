"""
Create an xml point source library from an ascii file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header: /nfs/slac/g/glast/ground/cvs/likeGui/python/ObsSim/create_library.py,v 1.2 2005/10/31 01:32:24 jchiang Exp $
#

import sys, os

_ptsrc_template = """<source name="%s" flux="%.3e">
   <spectrum escale="MeV">
      <particle name="gamma">
         <power_law emin="%.1f" emax="%.1f" gamma="%.2f" %s/>
      </particle>
      <celestial_dir ra="%.2f" dec="%.2f" />
   </spectrum>
</source>
"""

def ptsrc(name, ra, dec, flux, gamma, gamma2=None, ebreak=2e3,
          emin=20, emax=1e6):
    if gamma2 is not None:
        bpl = 'gamma2="%.2f" ebreak="%.1f" ' % (float(gamma2), float(ebreak))
    else:
        bpl = ''
    return _ptsrc_template % (name, float(flux), float(emin),
                              float(emax), float(gamma), bpl,
                              float(ra), float(dec))

def nested_sources(names, libname):
    lines = ['<source name="all_sources_in_%s">' % libname]
    for name in names:
        lines.append('   <nestedSource sourceRef="%s" />' % name)
    lines.append('</source>')
    return lines

def makeSrcLib(inputfile):
    infile = open(inputfile, 'r')
    lines = [line.strip() for line in infile.readlines()
             if line.find('#') != 0]
    outlines = ['<source_library title="%s">\n' % os.path.basename(inputfile)]
    names = []
    for line in lines:
        data = line.split()
        if len(data) > 4:
            outlines.append(ptsrc(*data[:9]))
            names.append(data[0])
    outlines.extend(nested_sources(names, os.path.basename(inputfile)))
    outlines.append('</source_library>')
    return outlines

if __name__ == '__main__':
    import sys
    if sys.argv[1:2]:
        infile = sys.argv[1]
    else:
        infile = "srclib.txt"
    items = makeSrcLib(infile)
    if sys.argv[2:3]:
        outfile = open(sys.argv[2], 'w')
        for item in items:
            outfile.write(item + '\n')
        outfile.close()
    else:
        for item in items:
            print item
