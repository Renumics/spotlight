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
          poetry
          pre-commit
          nodejs_20
          pnpm
          shellcheck
          shfmt
        ];
        shellHook = ''
          echo "Welcome to the Spotlight Development Environment!"
        '';
      };
    };
}
