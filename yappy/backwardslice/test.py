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
