/**
 * @file ModelEditor.cxx
 * @brief Driver for running ModelEditor
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header: /nfs/slac/g/glast/ground/cvs/likeGui/src/ModelEditor.cxx,v 1.1 2005/08/26 21:34:52 jchiang Exp $
 */

#include <cstdlib>

#include <iostream>
#include <string>

int main(int iargc, char *argv[]) {
   std::string command;
   char * root_path = std::getenv("LIKEGUIROOT");
   if (root_path == 0) {
      std::cerr << "Environment variable LIKEGUIROOT not found." << std::endl;
      return 1;
   }
   std::string pythonDir = std::string(root_path) + "/python";
   command = std::string("python ") + pythonDir + "/ModelEditor.py ";
   if (iargc > 1) {
      command += std::string(argv[1]);
   }
   std::system(command.c_str());
}
