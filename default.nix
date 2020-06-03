with import <nixpkgs> {};

let
  requirements = import ./requirements.nix;
in
  buildEnv {
    name = "python-env";
    paths = [requirements];
  }
