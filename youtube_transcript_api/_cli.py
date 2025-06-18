import argparse
from typing import List

from .proxies import GenericProxyConfig, WebshareProxyConfig
from .formatters import FormatterLoader

from ._api import YouTubeTranscriptApi, FetchedTranscript, TranscriptList


class YouTubeTranscriptCli:
    def __init__(self, args: List[str]):
        self._args = args

    def run(self) -> str:
        parsed_args = self._parse_args()

        if parsed_args.exclude_manually_created and parsed_args.exclude_generated:
            return ""

        proxy_config = None
        if parsed_args.http_proxy != "" or parsed_args.https_proxy != "":
            proxy_config = GenericProxyConfig(
                http_url=parsed_args.http_proxy,
                https_url=parsed_args.https_proxy,
            )

        if (
            parsed_args.webshare_proxy_username is not None
            or parsed_args.webshare_proxy_password is not None
        ):
            proxy_config = WebshareProxyConfig(
                proxy_username=parsed_args.webshare_proxy_username,
                proxy_password=parsed_args.webshare_proxy_password,
            )

        transcripts = []
        exceptions = []
        search_results_output = []

        ytt_api = YouTubeTranscriptApi(
            proxy_config=proxy_config,
        )

        for video_id in parsed_args.video_ids:
            try:
                transcript_list = ytt_api.list(video_id)
                if parsed_args.list_transcripts:
                    transcripts.append(transcript_list)
                elif parsed_args.search:
                    fetched_transcript = self._fetch_transcript(
                        parsed_args,
                        transcript_list,
                    )
                    search_results = fetched_transcript.search_in_transcript(
                        parsed_args.search,
                        case_sensitive=parsed_args.case_sensitive,
                        use_regex=parsed_args.regex,
                    )
                    search_results_output.append(
                        self._format_search_results(search_results, video_id)
                    )
                else:
                    transcripts.append(
                        self._fetch_transcript(
                            parsed_args,
                            transcript_list,
                        )
                    )
            except Exception as exception:
                if parsed_args.search:
                    search_results_output.append(str(exception))
                else:
                    exceptions.append(exception)

        if parsed_args.search:
            return "\n\n".join(search_results_output)

        print_sections = [str(exception) for exception in exceptions]
        if transcripts:
            if parsed_args.list_transcripts:
                print_sections.extend(
                    str(transcript_list) for transcript_list in transcripts
                )
            else:
                print_sections.append(
                    FormatterLoader()
                    .load(parsed_args.format)
                    .format_transcripts(transcripts)
                )

        return "\n\n".join(print_sections)

    def _fetch_transcript(
        self,
        parsed_args,
        transcript_list: TranscriptList,
    ) -> FetchedTranscript:
        if parsed_args.exclude_manually_created:
            transcript = transcript_list.find_generated_transcript(
                parsed_args.languages
            )
        elif parsed_args.exclude_generated:
            transcript = transcript_list.find_manually_created_transcript(
                parsed_args.languages
            )
        else:
            transcript = transcript_list.find_transcript(parsed_args.languages)

        if parsed_args.translate:
            transcript = transcript.translate(parsed_args.translate)

        return transcript.fetch()

    def _format_search_results(self, search_results, video_id):
        """Format search results for CLI output."""
        if not search_results:
            return f"No search results found for video {video_id}"

        formatted_results = [f"Search results for video {video_id}:"]
        for i, result in enumerate(search_results, 1):
            formatted_results.append(
                f"\n{i}. [{result.start_time:.2f}s - {result.end_time:.2f}s] "
                f'"{result.matched_text}"\n   Context: {result.context}'
            )

        return "\n".join(formatted_results)

    def _parse_args(self):
        parser = argparse.ArgumentParser(
            description=(
                "This is an python API which allows you to get the transcripts/subtitles for a given YouTube video. "
                "It also works for automatically generated subtitles and it does not require a headless browser, like "
                "other selenium based solutions do!"
            )
        )
        parser.add_argument(
            "--list-transcripts",
            action="store_const",
            const=True,
            default=False,
            help="This will list the languages in which the given videos are available in.",
        )
        parser.add_argument(
            "video_ids", nargs="+", type=str, help="List of YouTube video IDs."
        )
        parser.add_argument(
            "--languages",
            nargs="*",
            default=[
                "en",
            ],
            type=str,
            help=(
                'A list of language codes in a descending priority. For example, if this is set to "de en" it will '
                "first try to fetch the german transcript (de) and then fetch the english transcript (en) if it fails "
                "to do so. As I can't provide a complete list of all working language codes with full certainty, you "
                "may have to play around with the language codes a bit, to find the one which is working for you!"
            ),
        )
        parser.add_argument(
            "--exclude-generated",
            action="store_const",
            const=True,
            default=False,
            help="If this flag is set transcripts which have been generated by YouTube will not be retrieved.",
        )
        parser.add_argument(
            "--exclude-manually-created",
            action="store_const",
            const=True,
            default=False,
            help="If this flag is set transcripts which have been manually created will not be retrieved.",
        )
        parser.add_argument(
            "--format",
            type=str,
            default="pretty",
            choices=tuple(FormatterLoader.TYPES.keys()),
        )
        parser.add_argument(
            "--translate",
            default="",
            help=(
                "The language code for the language you want this transcript to be translated to. Use the "
                "--list-transcripts feature to find out which languages are translatable and which translation "
                "languages are available."
            ),
        )
        parser.add_argument(
            "--webshare-proxy-username",
            default=None,
            type=str,
            help='Specify your Webshare "Proxy Username" found at https://dashboard.webshare.io/proxy/settings',
        )
        parser.add_argument(
            "--webshare-proxy-password",
            default=None,
            type=str,
            help='Specify your Webshare "Proxy Password" found at https://dashboard.webshare.io/proxy/settings',
        )
        parser.add_argument(
            "--http-proxy",
            default="",
            metavar="URL",
            help="Use the specified HTTP proxy.",
        )
        parser.add_argument(
            "--https-proxy",
            default="",
            metavar="URL",
            help="Use the specified HTTPS proxy.",
        )
        parser.add_argument(
            "--search",
            default="",
            type=str,
            help="Search for a keyword or phrase within the transcript text.",
        )
        parser.add_argument(
            "--regex",
            action="store_const",
            const=True,
            default=False,
            help="Treat the search term as a regular expression pattern.",
        )
        parser.add_argument(
            "--case-sensitive",
            action="store_const",
            const=True,
            default=False,
            help="Perform case-sensitive search (default is case-insensitive).",
        )
        # Cookie auth has been temporarily disabled, as it is not working properly with
        # YouTube's most recent changes.
        # parser.add_argument(
        #     "--cookies",
        #     default=None,
        #     help="The cookie file that will be used for authorization with youtube.",
        # )

        return self._sanitize_video_ids(parser.parse_args(self._args))

    def _sanitize_video_ids(self, args):
        args.video_ids = [video_id.replace("\\", "") for video_id in args.video_ids]
        return args
