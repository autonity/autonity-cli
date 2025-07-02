{ pkgs, ... }:

{
  packages = [
    pkgs.hatch
    pkgs.taplo
  ];

  languages.python = {
    enable = true;
    version = "3.12";
    venv.enable = false;
  };
}
