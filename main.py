from args import parse_arguments
from processing import process_video_feed


if __name__ == "__main__":
    args = parse_arguments()
    process_video_feed(args.rtsp, args.output)
