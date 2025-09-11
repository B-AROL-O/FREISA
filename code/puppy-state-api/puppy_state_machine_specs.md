# Puppy State Machine

The puppy has an internal state that determines what face is shown in the display. In the future this could be extended to other behaviours, such as emitting sounds or making certain movements.

This documents describes the possible states and the state transitions.

## State Diagram

![Puppy State Diagram](assets/images/puppy-state-diagram-v1.png "Puppy State Diagram")

## States

- **Idle**: Sleepy / Resting face; the puppy is not active and it's waiting for activation command.

- **Listening**: the puppy received the activation command and it's waiting for a command.

- **Thinking**: the command has been received and the LLM is computing the response.

- **Happy/Wink**: the command was valid and the LLM produced a valid instruction for the puppy.

- **Confused**: the command was not valid and the LLM produced an error response or an invalid instruction.

- **Happy/Proud**: the puppy successfully executed the command.

## Transitions

- _Idle → Listening_

  **Event**: "Hello puppy" detected

- _Listening → Thinking_:

  **Event**: Command received (speech-to-text recognized)

- _Thinking → Happy/Wink_:

  **Event**: LLM returns valid instruction JSON

- _Thinking → Confused_:

  **Event**: LLM returns invalid or no instructions

- _Happy/Wink → Happy/Proud_:

  **Event**: Puppy executes action successfully

- _Confused → Idle_:

  **Event**: 5 seconds timeout

- _Happy/Proud → Idle_:

  **Event**: 5 seconds timeout
