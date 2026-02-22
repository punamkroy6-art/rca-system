{ pkgs }: {
	deps = [
		pkgs.python311
		pkgs.python311Packages.pip
		pkgs.libxcrypt
		pkgs.tk
		pkgs.tcl
		pkgs.freetype
		pkgs.libpng
	];
}
