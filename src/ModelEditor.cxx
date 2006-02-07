/**
 * @file ModelEditor.cxx
 * @brief Driver for running ModelEditor
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header: /nfs/slac/g/glast/ground/cvs/likeGui/src/ModelEditor.cxx,v 1.2 2005/09/19 00:20:21 jchiang Exp $
 */

#include <cstdlib>

#include <iostream>
#include <string>

int main(int iargc, char *argv[]) {
   std::string command 
      = "python -c \"import ModelEditor; ModelEditor.ModelEditor()\"";
   std::system(command.c_str());
}
