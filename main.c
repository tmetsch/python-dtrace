/*
 * Simple test to see how libdtrace works - will be used to create the Python
 * code later on...
 */

#include <stdio.h>
#include <stdlib.h>
#include <dtrace.h>

static int
chew(const dtrace_probedata_t *data, void *arg)
{
	dtrace_probedesc_t *probedesc = data->dtpda_pdesc;
	processorid_t cpu = data->dtpda_cpu;
	fprintf(stdout, "%2d %2d %10s %10s", cpu, probedesc->dtpd_id, probedesc->dtpd_provider, probedesc->dtpd_name);
	return (DTRACE_CONSUME_THIS);
}

static int
chewrec(const dtrace_probedata_t *data, const dtrace_recdesc_t *rec, void *arg)
{
	if (rec == NULL) {
		fprintf(stdout, "\n");
		return (DTRACE_CONSUME_NEXT);
	}
	return (DTRACE_CONSUME_THIS);
}

static int
buffered(const dtrace_bufdata_t *bufdata, void *arg)
{
	fprintf(stdout, " %s", bufdata->dtbda_buffered);
	return (DTRACE_HANDLE_OK);
}

/*
 * there we go...
 */
int
main(int argc, char** argv)
{
	int err = 0;

	// Get DTrace handle.
	dtrace_hdl_t *handle;
	handle = dtrace_open(DTRACE_VERSION, 0, &err);
	if (handle == NULL) {
		fprintf(stderr, "Unable to get hold of an dtrace handle: %s\n", dtrace_errmsg(NULL, err));
	}

	// set options
	if (dtrace_setopt(handle, "bufsize", "4m") != 0) {
		fprintf(stderr, "Unable to set bufsize option: %s\n", dtrace_errmsg(NULL, err));
	}

	// set buffer
	if (dtrace_handle_buffered(handle, buffered, NULL) == -1) {
		fprintf(stderr, "Unable to add buffered output: %s\n", dtrace_errmsg(NULL, err));
	}

	// compile from string.
	dtrace_prog_t *prog;
	char *script = "dtrace:::BEGIN {trace(\"Hello World\");}";

	prog = dtrace_program_strcompile(handle, script, DTRACE_PROBESPEC_NAME, DTRACE_C_ZDEFS, 0, NULL);
	fprintf(stderr, "%d", DTRACE_C_ZDEFS);
	if (prog == NULL) {
		fprintf(stderr, "Unable to compile d script: %s\n", dtrace_errmsg(NULL, err));
	}

	// run
	dtrace_proginfo_t info;
	dtrace_program_exec(handle, prog, &info);
	dtrace_go(handle);

	dtrace_stop(handle);

	// aggregate
	dtrace_sleep(handle);
	FILE *outfile;
	outfile = fopen("out.txt", "w");
	//dtrace_work(handle, outfile, chew, chewrec, NULL);
	// with None -> buffered writer
	dtrace_work(handle, NULL, chew, chewrec, NULL);

	// Print errors if any...
	fprintf(stderr, dtrace_errmsg(handle, dtrace_errno(handle)));

	// Close the DTrace handle.
	dtrace_close(handle);

	return (EXIT_SUCCESS);
}

