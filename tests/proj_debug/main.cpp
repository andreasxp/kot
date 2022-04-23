#include <iostream>

int main() {
#ifndef NDEBUG
	std::cout << "debug";
#else
	std::cout << "release";
#endif
}