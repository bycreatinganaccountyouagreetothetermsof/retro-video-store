# TODO:
- break out missing_field error into function
- sanitize request inputs that get passed into constructors
- research globals and pull out model selection logic
- simplify other selection logic
- add docstrings
- maybe undo some of the more efficient reuse, it's just a lot of conditionals
- better tests?
- integrityerror logic might hit on spurious nones instead of intended fields
- ~~cli app~~
- stop redudant inventory decrement per rental on video deletion
- make rental dict format switch on counterpart instead of model
- clarify comprehension performing rental/history selection
- rescue sorcery from the depths of galvanize. does editing a dockerfile violate
  the CFAA?
- ~~sleep~~

## rvsclient

repo contains a command line app for interacting with the retro-video-store api

it has a switchable default "human" and --json output option

for testing, the requests package gets mocked from within the flask app, so it
can run against a real server. this was actually the hardest part to figure out

## CLI TODO:
- implement "at least one required" option and double-filtering logic on rentals
  active and rentals history commands
- more json tests
- nicer text output formatting
- more dynamic indentation on human output
- try running it by hand against a heroku instance
- all POST and other non-GET functionality
