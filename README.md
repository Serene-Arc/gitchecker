# gitchecker

Do you embody ADHD? Do you have lots of projects that you keep picking up and putting down? Do you leave repositories with a bunch of unchanged files, or do you just keep forgetting to push all those changes once you've committed them? Well fear no more!

This is a simple Python tool mean to tell you the status of each of the repositories in your projects folder. If the branch is ahead or behind, or if there are uncommitted or staged files, the tool will show that status message along with the path of the repo in question. Makes keeping track of everything a whole lot easier, and reminds you not to keep outstanding work laying around. 

The gitchecker can be recursive and check all git repositories in a tree or just a single folder, as required.

## Options and Arguments

- `directories` 
  - Directories to search
  - Multiple directories can be specified
- `-r, --recursive`
  - Turns on recursive mode