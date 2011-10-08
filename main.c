/*
 * Simple test to see how libdtrace works - will be used to create the Python
 * code later on...
 */

#include <stdio.h>
#include <stdlib.h>
#include <dtrace.h>
#include <unistd.h>

static int
chew(const dtrace_probedata_t *data, void *arg)
{
	dtrace_probedesc_t *probedesc = data->dtpda_pdesc;
	processorid_t cpu = data->dtpda_cpu;
	fprintf(stdout, "+--> in chew: %2d %2d %10s %10s", cpu, probedesc->dtpd_id, probedesc->dtpd_provider, probedesc->dtpd_name);
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
	fprintf(stdout, " +--> In buffered: %s", bufdata->dtbda_buffered);
	return (DTRACE_HANDLE_OK);
}

/*
 * DTrace aggregate walker use this instead of chew, chewrec and buffered (which just output printf)...
 */
static int
walk(const dtrace_aggdata_t *data, void *arg)
{
	dtrace_aggdesc_t *aggdesc = data->dtada_desc;
	dtrace_recdesc_t *nrec, *irec;
	char *name;
	int32_t *instance;
	static const dtrace_aggdata_t *count;

	if (count == NULL) {
		count = data;
		return (DTRACE_AGGWALK_NEXT);
	}

	nrec = &aggdesc->dtagd_rec[1];
	irec = &aggdesc->dtagd_rec[2];

	name = data->dtada_data + nrec->dtrd_offset;
	instance = (int32_t *) (data->dtada_data + irec->dtrd_offset);

	fprintf(stderr, "+--> In walk: %-20s %-10d\n", name, *instance);

	return (DTRACE_AGGWALK_NEXT);
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
	if (dtrace_setopt(handle, "aggsize", "4m") != 0) {
		fprintf(stderr, "Unable to set bufsize option: %s\n", dtrace_errmsg(NULL, err));
	}

	// set buffer
	if (dtrace_handle_buffered(handle, buffered, NULL) == -1) {
		fprintf(stderr, "Unable to add buffered output: %s\n", dtrace_errmsg(NULL, err));
	}

	// compile from string.
	dtrace_prog_t *prog;
	char *script2 = "dtrace:::BEGIN {trace(\"Hello World\");} syscall:::entry { @num[execname] = count(); }";

	prog = dtrace_program_strcompile(handle, script2, DTRACE_PROBESPEC_NAME, DTRACE_C_ZDEFS, 0, NULL);
	if (prog == NULL) {
		fprintf(stderr, "Unable to compile d script: %s\n", dtrace_errmsg(NULL, err));
	}

	// run
	dtrace_proginfo_t info;
	dtrace_program_exec(handle, prog, &info);
	dtrace_go(handle);

	// aggregate for a few secs
	int i = 0;
	do {
		dtrace_sleep(handle);
		dtrace_work(handle, NULL, chew, chewrec, NULL);
		sleep(1);
		i += 1;
	} while (i < 10);
	dtrace_stop(handle);

	if (dtrace_aggregate_snap(handle) != 0)
		printf("failed to add to aggregate\n");

	// Instead of print -> we'll walk...dtrace_aggregate_print(handle, stdout, NULL);
	if (dtrace_aggregate_walk_valsorted(handle, walk, NULL) != 0) {
		fprintf(stderr, "Unable to append walker: %s\n", dtrace_errmsg(NULL, err));
	}

	// Print errors if any...
	fprintf(stderr, dtrace_errmsg(handle, dtrace_errno(handle)));

	// Close the DTrace handle.
	dtrace_close(handle);

	return (EXIT_SUCCESS);
}
