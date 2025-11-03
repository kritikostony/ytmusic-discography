{
  description = "Multi-machine NixOS configuration for Tony";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
  };

  outputs = { self, nixpkgs, ... }:
    let
      mkHost = hostModule:
        nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          modules = [ hostModule ];
        };
    in {
      nixosConfigurations = {
        tony-server = mkHost ./hosts/tony-server/default.nix;
        tony-backup-server = mkHost ./hosts/tony-backup-server/default.nix;
        tony-laptop = mkHost ./hosts/tony-laptop/default.nix;
        tony-download-laptop = mkHost ./hosts/tony-download-laptop/default.nix;
      };

      formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.nixpkgs-fmt;
    };
}
