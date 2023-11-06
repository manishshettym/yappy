def download(channel_url, language, number_of_jobs):
    console = Console()
    s = requests.session()

    # find out if the channel exists on the internet
    with console.status("[bold green]Getting Channel ID...") as status:
        channel_url = validate_channel_url(channel_url)
        handle_reject_consent_cookie(channel_url, s)
        channel_id = get_channel_id(channel_url, s)

    if channel_id is None:
        console.print(
            "[bold red]Error:[/bold red] Invalid channel URL or unable to extract channel ID."
        )
        return

    """__Schrodinger's Channel ID__

    Alright, Now that we know it exists on the internet, let's find out 
    if we had it all along to begin with! What's that you're saying? 
    We should have checked this before making the request? Well, that's 
    just because you're not thinking like a 10x developer.
    
    You see, I program in a state of quantum superposition. 
    
    While you might think it's more efficient to check if the data exists 
    in the local database before wasting bandwidth making a request to 
    the internet. A Superpositionist, such as myself, knows that the data 
    actually exists in both states at the same time! 
     
    However, it is only when we observe the data that it collapses into a 
    single state. And because our database was designed in such brilliant 
    way that we must first observe remote data to actually know if it exists,

    one might say that. 

    We are in a state of quantum entanglement with the data.
 
    """
    channel_exists = check_if_channel_exists(channel_id)

    if channel_exists:
        list_channels(channel_id)
        error = "[bold red]Error:[/bold red] Channel already exists in database."
        error += " Use update command to update the channel"
        console.print(error)
        return

    handle_reject_consent_cookie(channel_url, s)
    channel_name = get_channel_name(channel_id, s)

    if channel_name is None:
        console.print("[bold red]Error:[/bold red] The channel does not exist.")
        return

    download_channel(channel_id, channel_name, language, number_of_jobs, s)
