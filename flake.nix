{
  description = "Multi-machine NixOS configuration for Tony";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs, ... }:
    let
      mkHost = hostModule:
        nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          modules = [ hostModule ];
        };
    in {
      # Custom command that runs rebuild
      packages.x86_64-linux.tony-nixos =
        nixpkgs.legacyPackages.x86_64-linux.writeShellScriptBin "tony-nixos" ''
          sudo nixos-rebuild switch --flake /etc/nixos-config
        '';
      nixosConfigurations = {
        tony-server = mkHost ./hosts/tony-server/default.nix;
        tony-backup-server = mkHost ./hosts/tony-backup-server/default.nix;
        tony-laptop = mkHost ./hosts/tony-laptop/default.nix;
        tony-download-laptop = mkHost ./hosts/tony-download-laptop/default.nix;
      };

      formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.nixpkgs-fmt;
    };
}
