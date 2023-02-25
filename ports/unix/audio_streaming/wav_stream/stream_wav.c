#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <float.h>

#include <stdbool.h>
#include <stdlib.h>
#include <strings.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>

#include <sndfile.h>

#define	BLOCK_SIZE 4096

#ifdef DBL_DECIMAL_DIG
	#define OP_DBL_Digs (DBL_DECIMAL_DIG)
#else
	#ifdef DECIMAL_DIG
		#define OP_DBL_Digs (DECIMAL_DIG)
	#else
		#define OP_DBL_Digs (DBL_DIG + 3)
	#endif
#endif

void error(char *msg) {
	perror(msg);
	exit(0);
}

static void
print_usage (char *progname)
{	printf ("\nUsage : %s <input file>\n", progname) ;
	puts ("\n"
		"    Where the output file will contain a line for each frame\n"
		"    and a column for each channel.\n"
		) ;

} /* print_usage */

static int
stream_out (SNDFILE * infile, int sockfd, int channels, int full_precision)
{	int *buf ;
	sf_count_t frames ;
	int k, m, readcount ;

	buf = malloc (BLOCK_SIZE * sizeof (int)) ;
	if (buf == NULL)
	{	printf ("Error : Out of memory.\n\n") ;
		return 1 ;
		} ;

	frames = BLOCK_SIZE / channels ;

	while (true) {
		while ((readcount = (int) sf_readf_int (infile, buf, frames)) > 0) {
			int n = write(sockfd, buf, readcount * sizeof(int)/sizeof(char));
			if (n < 0) {
				error("ERROR writing to socket");
			}
		};

		// reset to beginning of the soundfile
		sf_seek(infile, 0, SEEK_SET);
	}

	free (buf) ;

	return 0 ;
} /* convert_to_text */

int
main (int argc, char * argv [])
{	char 		*progname, *infilename, *outfilename ;
	SNDFILE		*infile = NULL ;
	SF_INFO		sfinfo ;
	int		full_precision = 0 ;
	int 	ret = 1 ;

	progname = strrchr (argv [0], '/') ;
	progname = progname ? progname + 1 : argv [0] ;

	if (2 != argc) {
		printf("Unexpected number of arguments\n");
		print_usage (progname) ;
		goto cleanup ;
	}

	infilename = argv [1] ;

	if (infilename [0] == '-')
	{	printf ("Error : Input filename (%s) looks like an option.\n\n", infilename) ;
		print_usage (progname) ;
		goto cleanup ;
		} ;

	memset (&sfinfo, 0, sizeof (sfinfo)) ;

	if ((infile = sf_open (infilename, SFM_READ, &sfinfo)) == NULL)
	{	printf ("Not able to open input file %s.\n", infilename) ;
		puts (sf_strerror (NULL)) ;
		goto cleanup ;
		} ;

	// open a socket 
	int portno = 42310; // serve audio stream on port 42310
	int sockfd, newsockfd, clilen;
	struct sockaddr_in serv_addr, cli_addr;
	int n;
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		error("ERROR opening socket");
	}
	bzero((char *) &serv_addr, sizeof(serv_addr));

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
		error("ERROR on binding");
	}
	listen(sockfd,5);
	clilen = sizeof(cli_addr);
	newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
	if (newsockfd < 0) {
		error("ERROR on accept");
	}

	// use that socket to stream out
	ret = stream_out (infile, newsockfd, sfinfo.channels, full_precision) ;

cleanup:

	sf_close (infile) ;

	return ret ;
} /* main */

