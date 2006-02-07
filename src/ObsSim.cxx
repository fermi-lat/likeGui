/**
 * @file ObsSim.cxx
 * @brief Driver for running ObsSim
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header: /nfs/slac/g/glast/ground/cvs/likeGui/src/ObsSim.cxx,v 1.2 2005/09/19 00:20:22 jchiang Exp $
 */

#include <cstdlib>

#include <iostream>
#include <string>

int main() {
   std::string command("python -c \"import ObsSim; ObsSim.ObsSim()\"");
   std::system(command.c_str());
}
