#include <iostream>
#include <boost/container/flat_map.hpp> // If boost is installed, this will be found

int main() {
	boost::container::flat_map<int, int> fl;
	std::cout << "Hello World!\n";
}