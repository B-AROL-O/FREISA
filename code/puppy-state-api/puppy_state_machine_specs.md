# Puppy State Machine

The puppy has an internal state that determines what face is shown in the display. In the future this could be extended to other behaviours, such as emitting sounds or making certain movements.

This documents describes the possible states and the state transitions.

## State Diagram

![Puppy State Diagram](assets/images/puppy-state-diagram-v1.png "Puppy State Diagram")

## States

* __Idle__: Sleepy / Resting face; the puppy is not active and it's waiting for activation command.

* __Listening__: the puppy received the activation command and it's waiting for a command.

* __Thinking__: the command has been received and the LLM is computing the response.

* __Happy/Wink__: the command was valid and the LLM produced a valid instruction for the puppy.

* __Confused__: the command was not valid and the LLM produced an error response or an invalid instruction.

* __Happy/Proud__: the puppy successfully executed the command.

## Transitions

* _Idle → Listening_

    __Event__: "Hello puppy" detected

* _Listening → Thinking_:

    __Event__: Command received (speech-to-text recognized)

* _Thinking → Happy/Wink_:

    __Event__: LLM returns valid instruction JSON

* _Thinking → Confused_:

    __Event__: LLM returns invalid or no instructions

* _Happy/Wink → Happy/Proud_:

    __Event__: Puppy executes action successfully

* _Confused → Idle_:

    __Event__: 5 seconds timeout

* _Happy/Proud → Idle_:

    __Event__: 5 seconds timeout
