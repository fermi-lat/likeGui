/**
 * @file likeGui.cxx
 * @brief Driver for running likeGui
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header: /nfs/slac/g/glast/ground/cvs/likeGui/src/likeGui.cxx,v 1.2 2005/09/19 00:20:22 jchiang Exp $
 */

#include <cstdlib>

#include <iostream>
#include <string>

int main(int iargc, char *argv[]) {
   std::string command("python -c \"import likeGui; likeGui.likeGui()\"");
   std::system(command.c_str());
}
