def parse_petri_net_file(filepath):
    """parses Petri net data from file of specified format"""
    places = []
    initial_marking = {}
    transitions = {}
    
    current_section = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # skip comments, empty lines
            if not line or line.startswith('#'):
                continue
            
            # section logic
            if line.upper() == "[PLACES]":
                current_section = "P"
                continue
            elif line.upper() == "[TRANSITIONS]":
                current_section = "T"
                continue
            
            if current_section == "P":
                # expected format: "place: initialTokens"
                name, tokens = line.split(':')
                name = name.strip()
                places.append(name)
                initial_marking[name] = int(tokens.strip())
                
            elif current_section == "T":
                # expected format: "transition : P1:1, P2:2 -> P3:1"
                # space after transition mandatory!
                try:
                    name_part, flow_part = line.split(' : ')
                    name = name_part.strip()
                    
                    inputs, outputs = flow_part.split('->')
                    
                    def parse_weights(s):
                        weights = {}
                        parts = [p.strip() for p in s.split(',') if p.strip()]
                        for p in parts:
                            p_name, weight = p.split(':')
                            weights[p_name.strip()] = int(weight.strip())
                        return weights

                    transitions[name] = (
                        parse_weights(inputs),
                        parse_weights(outputs)
                    )
                except ValueError:
                    print(f"malformed line: {line}")

    return places, initial_marking, transitions