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
	    modules = [
	      hostModule
	      # Inject overlay so pkgs.tony-nixos exists
	      ({ pkgs, ... }: {
	        nixpkgs.overlays = [ self.overlays.default ];
	      })
              # Load secret file even if it's in .gitignore
              /etc/nixos/secret.nix
	    ];
	  };
    in {
      # Custom rebuild command
      packages.x86_64-linux.tony-nixos =
        nixpkgs.legacyPackages.x86_64-linux.writeShellScriptBin "tony-nixos" ''
          sudo nixos-rebuild switch --flake /etc/nixos-config
        '';
      # Overlay to expose the package as pkgs.tony-nixos
      overlays = {
        default = final: prev: {
          tony-nixos = self.packages.${prev.system}.tony-nixos;
        };
      };
      nixosConfigurations = {
        tony-server = mkHost ./hosts/tony-server/default.nix;
        tony-backup-server = mkHost ./hosts/tony-backup-server/default.nix;
        tony-laptop = mkHost ./hosts/tony-laptop/default.nix;
        tony-download-laptop = mkHost ./hosts/tony-download-laptop/default.nix;
      };

      formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.nixpkgs-fmt;
    };
}
