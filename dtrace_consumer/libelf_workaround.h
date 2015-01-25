/*
 * Needed to resolve: http://gcc.gnu.org/bugzilla/show_bug.cgi?id=39019
 */

#if defined(_ILP32) && (_FILE_OFFSET_BITS != 32)
#define _FILE_OFFSET_BITS 32
#endif
