{
  pkgs,
  lib,
  config,
  ...
}:

{
  packages = [
    pkgs.hatch
    pkgs.taplo
    pkgs.libusb1
  ];

  env.HATCH_PYTHON = "${config.env.DEVENV_PROFILE}/bin/python";
  env.LD_LIBRARY_PATH = lib.makeLibraryPath [
    pkgs.libusb1
  ];

  languages.python = {
    enable = true;
    version = "3.13"; # must match `pkgs.hatch` python version
    venv.enable = false;
  };
}
