with import <nixpkgs> {};

let
  requirements = import ./requirements.nix;
in
  mkShell {
    buildInputs = [requirements];
  }
