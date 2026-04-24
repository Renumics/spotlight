{
  description = "Spotlight Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        name="spotlight-dev-shell";
        packages = with pkgs; [
          python312
          uv
          pre-commit
          nodejs_20
          pnpm
          shellcheck
          shfmt
          stdenv.cc.cc.lib
        ];
        shellHook = ''
          unset SOURCE_DATE_EPOCH
          export UV_PYTHON=${pkgs.python312}/bin/python
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
          ]}:$LD_LIBRARY_PATH
          echo "Welcome to the Spotlight Development Environment!"
        '';
      };
    };
}
