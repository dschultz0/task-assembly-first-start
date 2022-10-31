def process_response(event, context):
    return event.get('numberAsText')


def consolidate_result(event, context):
    try:
        print(event)
        responses = event.get('Responses')

        # Just return the first assignment when using the Sandbox
        if event.get('Sandbox'):
            return {'value': responses[0]['Result']['value']}

        # Score how often each of the responses is returned
        scored_values = {}
        for response in responses:
            # normalize by changing to lowercase and trimming spaces
            value = str(response['Result']['value']).lower().strip()
            # ignore responses that are just numbers
            if not value.isnumeric():
                scored_values[value] = scored_values.get(value, 0) + 1

        print(scored_values)

        for response, score in scored_values.items():
            # if two people agree, accept it
            if score >= 2:
                return {'value': response}
        return {'extend': True}
    except Exception as e:
        print(e)
        return {'error': e.args[0]}
