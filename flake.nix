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
          nodejs_24
          pnpm_10
          shellcheck
          shfmt
          jdk21
          stdenv.cc.cc.lib
          ffmpeg_9-headless
          zlib
          chromium
          chromedriver
          firefox
          geckodriver
        ];
        shellHook = ''
          unset SOURCE_DATE_EPOCH
          # Nix Python packages (e.g. pre-commit) put their site-packages on
          # PYTHONPATH, which leaks into the project's virtual environment
          unset PYTHONPATH

          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib pkgs.zlib pkgs.ffmpeg_9-headless
          ]}:$LD_LIBRARY_PATH

          export PIP_IGNORE_INSTALLED=1

          # browsers matching the webdrivers above, used by the UI tests
          export CHROME_BIN=${pkgs.chromium}/bin/chromium
          export FIREFOX_BIN=${pkgs.firefox}/bin/firefox

          if [[ -d "./.venv" ]]; then
            VIRTUAL_ENV="$(pwd)/.venv"
          fi

          if [[ -z ''${VIRTUAL_ENV:-} || ! -d ''${VIRTUAL_ENV:-} ]]; then
            uv venv -p "$(command -v python3)"
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
