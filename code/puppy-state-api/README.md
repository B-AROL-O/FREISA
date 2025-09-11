# Puppy State API

An http server that provides an interface to manage the state of the puppy following
the specifics of a state machine.
The API also provides a way to explicitly display a specific face or play a sound,
bypassing the state machine.

## State machine specification

You can find the specifics of the state machine [here](./puppy_state_machine_specs.md).

## API specification

Endpoints:

- `GET /api/v1/states` - List available states
- `POST /api/v1/state` - Transition to new state
- `POST /api/v1/reset` - Reset to initial state
- `GET /api/v1/faces` - List available faces
- `POST /api/v1/face` - Set facial expression
- `GET /api/v1/sounds` - List available sounds
- `POST /api/v1/sound` - Play a sound

You can find the openapi specification file [here](./openapi.yml), to quickly
test the API with Postman or other tools.

## Configuration

Before running the code, you must adjust the puppy_config.json file according to
the state machine you want to implement and also to the images or sounds files
that you have available.

The config file has the following fields:

- `initialState`: the name of the initial state of the machine; must be
     in the list of possible states.
- `states`: the list of available states; each state has a unique name,
     an optional associated face, an optional associated sound and a
     list of states to which a valid transition is possible.
- `faces`: the list of available faces; each face has a unique name and
     a path where the image file is located.
- `sounds`: the list of available sounds; each sound has a unique name
     and a path where the audio file is located.

## Run the server

You can run the server just using uv command:

```bash
uv run main.py
```

## Test the API

You can test if the API is up and working by making http requests to it:

```bash
curl http://localhost:5000/api/v1/states
```

it should return the names of the available states.
