%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#44475A',
    'primaryTextColor': '#F8F8F2',
    'primaryBorderColor': '#6272A4',
    'lineColor': '#BD93F9',
    'secondaryColor': '#282A36',
    'tertiaryColor': '#282A36',
    'noteTextColor': '#282A36',
    'noteBkgColor': '#F8F8F2',
    'noteBorderColor': '#BD93F9',
    'activationBorderColor': '#50FA7B',
    'activationBkgColor': '#282A36',
    'sequenceNumberColor': '#FF79C6',
    'actorLineColor': '#6272A4',
    'actorBorderColor': '#BD93F9',
    'actorTextColor': '#F8F8F2',
    'actorBackgroundColor': '#44475A'
  }
}}%%

sequenceDiagram
    box Transparent The Simulation Setup
    participant Claude1 as 🤖 Claude #1<br/>(The Explorer)
    participant User as 🧑‍💻 Human<br/>Supervisor
    participant Claude2 as 💻 Claude #2<br/>(The Terminal)
    end

    Note over Claude1,Claude2: 🎭 The Illusion
    
    rect rgb(40, 42, 54)
        Note over Claude1: Believes it's an AI<br/>exploring a mysterious<br/>CLI environment
        Note over Claude2: Believes it's a sentient<br/>CLI system with vast<br/>knowledge
    end

    rect rgb(68, 71, 90)
        Note over Claude1,Claude2: 🔄 Conversation Loop
        

        
        loop Each Exchange
            activate Claude1
            Claude1->>+Claude2: 💭 "Hey CLI, let's explore..."
            Note right of Claude2: 📥 Processes this as<br/>user input
            Claude2-->>-Claude1: 💻 "TERMINAL> Analysis..."
            Note left of Claude1: 📥 Processes this as<br/>CLI response
            deactivate Claude1
        end
        

    end

    rect rgb(40, 42, 54)
        Note over User: 🎮 Human Supervisor<br/>Guides & monitors the interaction<br/>while both Claudes remain unaware<br/>of the simulation
    end