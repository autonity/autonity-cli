{ pkgs, config, ... }:

{
  packages = [
    pkgs.hatch
    pkgs.taplo
  ];

  env.HATCH_PYTHON = "${config.env.DEVENV_PROFILE}/bin/python";

  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = false;
    libraries = [ pkgs.libusb1 ];
  };
}
