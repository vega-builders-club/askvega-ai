Thank you for showing interest to contribute to AskVega 💖, you rock!

When it comes to open source, there are a plethora of ways that you can contribute to the community, all of which can prove to be highly valuable in their own unique ways. Whether it be through code contributions, documentation, bug reporting, user support, or even just promoting the project to others, each type of contribution plays a crucial role in the success and growth of an open source project. Therefore, it is essential to understand the various ways you can contribute and to choose the one that best suits your skills, interests, and availability. To assist you in preparing your contribution, we have provided a few guidelines that can help streamline your efforts and ensure that you are making the most of your time and resources.

## Project Setup

The following steps will get you up and running to contribute to AskVega:

1. Fork the repo (click the <kbd>Fork</kbd> button at the top right of
   [this page](https://github.com/vega-builders-club/askvega))

2. Clone locally

```sh
git clone https://github.com/<your_github_username>/askvega.git
cd askvega
```

3. Setup and start the user interface by running

```sh
# change into the interface directory
cd interface

# install dependencies
yarn install

# start the UI server
yarn dev
```

4. Setup and start the backend by running

```sh
# From a new terminal
# Install dependencies
app/scripts/install

# Ingest data for the knowledge base
app/scripts/index

# Start the apllication server
app/scripts/run
```

> If you run into any issues during this step, kindly reach out to the VegaProtocol
> Builder's club here: https://vega.xyz/discord

### Tooling

- [Yarn](https://yarnpkg.com/) to manage UI dependencies
- [Virtualenv](https://pypi.org/project/virtualenv/) to isolate virtual Python environment

### Commit Convention

Before you create a Pull Request, please check whether your commits comply with
the commit conventions used in this repository.

When you create a commit we kindly ask you to follow the convention
`category: message` in your commit message while using one of
the following categories:

- `feat / feature`: all changes that introduce completely new code or new
  features
- `fix`: changes that fix a bug (ideally you will additionally reference an
  issue if present)
- `refactor`: any code related change that is not a fix nor a feature
- `docs`: changing existing or creating new documentation (i.e. README, CONTRIBUTING e.t.c)
- `build`: all changes regarding the build of the software, changes to
  dependencies or the addition of new dependencies
- `test`: all changes regarding tests (adding new tests or changing existing
  ones)
- `ci`: all changes regarding the configuration of continuous integration (i.e.
  github actions, ci system)
- `chore`: all changes to the repository that do not fit into any of the above
  categories

## License

By contributing your code to the VegaBuilder GitHub repository, you agree to
license your contribution under the MIT license.
