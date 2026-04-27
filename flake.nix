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
          ffmpeg-headless
        ];
        shellHook = ''
          unset SOURCE_DATE_EPOCH

          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
          ]}:$LD_LIBRARY_PATH

          export UV_PYTHON=${pkgs.python312}/bin/python
          export PIP_IGNORE_INSTALLED=1

          if [[ -d "./.venv" ]]; then
            VIRTUAL_ENV="$(pwd)/.venv"
          fi

          if [[ -z ''${VIRTUAL_ENV:-} || ! -d ''${VIRTUAL_ENV:-} ]]; then
            uv venv
            VIRTUAL_ENV="$(pwd)/.venv"
          fi

          export PATH="$VIRTUAL_ENV/bin:$PATH"
          export UV_ACTIVE=1
          export VIRTUAL_ENV

          pre-commit install -f

          export SPOTLIGHT_DEV=True
          export SPOTLIGHT_VERBOSE=True
          export SPOTLIGHT_OPT_OUT=True
          VERSION="$(uv run uv-dynamic-versioning)"
          export VERSION

          echo "Welcome to the Spotlight Development Environment!"
        '';
      };
    };
}
