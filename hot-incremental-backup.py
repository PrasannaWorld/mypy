#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2006-2016 WANdisco,Inc. Pleasanton,CA,USA
# All rights reserved.
#
# Author: Jonathan Paul <support@wandisco.com>
#
#  hotincremental-backup.py: perform a "hot" backup of a Subversion 
#                 repository the first time it's called, and subsequently
#                 generate an incremental dump file.
#                 If the repository backend is Berkley DB, the old 
#                 Berkeley DB logfiles are cleaned up after the
#                 backup completes.
#
#                 This script is based on the hot-backup.py script
#                 Distributed in the tools directory of the subversion
#                 source repository
#
######################################################################

import sys, os, getopt, stat, re, time, shutil, subprocess

######################################################################
# Global Settings

# Path to svnlook utility
#svnlook = r"@SVN_BINDIR@/svnlook"
svnlook = "/usr/bin/svnlook"
# Path to svnadmin utility
svnadmin = "/usr/bin/svnadmin"

# Archive types/extensions
archive_map = {
  'gz'  : ".tar.gz",
  'bz2' : ".tar.bz2",
  }


######################################################################
# Command line arguments

def usage(out = sys.stdout):
  scriptname = os.path.basename(sys.argv[0])
  out.write(
"""USAGE: %s [OPTIONS] REPOS_PATH BACKUP_PATH

Create a backup of the repository at REPOS_PATH in a subdirectory of
the BACKUP_PATH location, named after the youngest revision. The
first backup is always a hotcopy, with subsequent backups being
incremental dump files.

Options:
  --archive-type=FMT Create an archive of the dumpfile backup. 
                     FMT can be one of:
                       bz2  : Creates a bzip2 compressed tar file.
                       gz   : Creates a gzip compressed tar file.
  --help      -h     Print this help message and exit.

""" % (scriptname,))


try:
  opts, args = getopt.gnu_getopt(sys.argv[1:], "h?", ["archive-type=",
                                                      "num-backups=",
                                                      "verify",
                                                      "help"])
except getopt.GetoptError, e:
  sys.stderr.write("ERROR: %s\n\n" % e)
  sys.stderr.flush()
  usage(sys.stderr)
  sys.exit(2)

archive_type = None
verify_copy = False

for o, a in opts:
  if o == "--archive-type":
    archive_type = a
  elif o in ("-h", "--help", "-?"):
    usage()
    sys.exit()

if len(args) != 2:
  sys.stderr.write("ERROR: only two arguments allowed.\n\n")
  sys.stderr.flush()
  usage(sys.stderr)
  sys.exit(2)

# Path to repository
repo_dir = args[0]
repo = os.path.basename(os.path.abspath(repo_dir))

# Where to store the repository backup.  The backup will be placed in
# a *subdirectory* of this location, named after the youngest
# revision.
backup_dir = args[1]

# Added to the filename regexp, set when using --archive-type.
ext_re = ""

# Do we want to create an archive of the backup
if archive_type:
  if archive_type in archive_map:
    # Additionally find files with the archive extension.
    ext_re = "(" + re.escape(archive_map[archive_type]) + ")?"
  else:
    sys.stderr.write("Unknown archive type '%s'.\n\n\n" % archive_type)
    sys.stderr.flush()
    usage(sys.stderr)
    sys.exit(2)


######################################################################
# Helper functions

def comparator(a, b):
  # We pass in filenames so there is never a case where they are equal.
  regexp = re.compile("-(?P<revision>[0-9]+)(-(?P<increment>[0-9]+))?" +
                      ext_re + "$")
  matcha = regexp.search(a)
  matchb = regexp.search(b)
  reva = int(matcha.groupdict()['revision'])
  revb = int(matchb.groupdict()['revision'])
  if (reva < revb):
    return -1
  elif (reva > revb):
    return 1
  else:
    inca = matcha.groupdict()['increment']
    incb = matchb.groupdict()['increment']
    if not inca:
      return -1
    elif not incb:
      return 1;
    elif (int(inca) < int(incb)):
      return -1
    else:
      return 1

def get_youngest_revision():
  """Examine the repository REPO_DIR using the svnlook binary
  specified by SVNLOOK, and return the youngest revision."""

  p = subprocess.Popen([svnlook, 'youngest', repo_dir],
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  infile, outfile, errfile = p.stdin, p.stdout, p.stderr

  stdout_lines = outfile.readlines()
  stderr_lines = errfile.readlines()
  outfile.close()
  infile.close()
  errfile.close()

  if stderr_lines:
    raise Exception("Unable to find the youngest revision for repository '%s'"
                    ": %s" % (repo_dir, stderr_lines[0].rstrip()))

  return stdout_lines[0].strip()

######################################################################
# Main

print("Beginning hot backup of '"+ repo_dir + "'.")


### Step 1: get the youngest revision.

try:
  youngest = get_youngest_revision()
except Exception, e:
  sys.stderr.write("%s\n" % e)
  sys.stderr.flush()
  sys.exit(1)

print("Youngest revision is %s" % youngest)

### Step 2: find last hotcopy
#   There must always be a hotcopy present. If there isn't then we create one

backup_subdir = os.path.join(backup_dir, repo + "-" + youngest)

directory_list = os.listdir(backup_dir)
#print("**DEBUG: directory_list is " + ", ".join(directory_list))

regexp = re.compile("^" + repo + "-(?P<last_youngest>[0-9]+)(-[0-9]+)?")

# We will always take the last hotcopy present as a starting revision for the incremental dump
hotcopy_list = [x for x in directory_list if regexp.search(x)]
#print("**DEBUG: hotcopy_list is " + ", ".join(hotcopy_list))

if hotcopy_list:
  hotcopy_list.sort(comparator)
  last_youngest = regexp.search(hotcopy_list.pop()).groupdict()['last_youngest']
else:
  # No previous hotcopies found, so we need to make one now
  print("Backing up repository to '" + backup_subdir + "'...")
  err_code = subprocess.call([svnadmin, "hotcopy", repo_dir, 
                            backup_subdir, "--clean-logs"])
  if err_code != 0:
    sys.stderr.write("Unable to backup the repository.\n")
    sys.stderr.flush()
    sys.exit(err_code)
  else:
    print("Done.")

  ### Always verify the hotcopy
  print("Verifying backup...")
  err_code = subprocess.call([svnadmin, "verify", "--quiet", backup_subdir])
  if err_code != 0:
    sys.stderr.write("Backup verification failed.\n")
    sys.stderr.flush()
    sys.exit(err_code)
  else:
    print("Done.")

  # optionally archive the hotcopy
  if archive_type:
    print("Archiving the hotcopy...")
    import tarfile
    tar = tarfile.open(backup_subdir + archive_map[archive_type], "w:" + archive_type)
    tar.add(backup_subdir, arcname=repo + "-" + youngest)
    tar.close()
    print("Done.")
    print("Removing original hotcopy dir...")
    shutil.rmtree(backup_subdir)
    print("Done.")

  # And now quit
  sys.exit(0)

### Step 3: Find next available dump file name

backup_dump = os.path.join(backup_dir, repo + "-" + youngest)

# If there is already a backup of this revision, then append the
# next highest increment to the path. We still need to do a backup
# because the repository might have changed despite no new revision
# having been created.

regexp = re.compile("^" + repo + "-" + youngest +
                    "(-(?P<increment>[0-9]+))?" + ext_re + "$")

file_list = os.listdir(backup_dir)
young_list = [x for x in file_list if regexp.search(x) and os.path.isfile(os.path.join(backup_dir,x))]
#print("**DEBUG: young_list is " + ", ".join(young_list))

if young_list:
  young_list.sort(comparator)
  increment = regexp.search(young_list.pop()).groupdict()['increment']
  if increment:
    backup_dump = os.path.join(backup_dir, repo + "-" + youngest + "-"
                                 + str(int(increment) + 1))
  else:
    backup_dump = os.path.join(backup_dir, repo + "-" + youngest + "-1")


### Step 4: find out the last youngest from dump file if it exists.
#           otherwise we use the last youngest from the hotcopy

regexp = re.compile("^" + repo + "-(?P<last_youngest>[0-9]+)(-[0-9]+)?" + ext_re + "$")
young_list = [x for x in file_list if regexp.search(x)]
if young_list:
  young_list.sort(comparator)
  last_youngest = regexp.search(young_list.pop()).groupdict()['last_youngest']
  # Need to check for the case when last_youngest == youngest, and go
  # further back
  while len(young_list) > 0  and int(last_youngest) == int(youngest):
    last_youngest = regexp.search(young_list.pop()).groupdict()['last_youngest']

### Step 5: Ask subversion to make an incremental dump file
# If there have been no changes at all since the hotcopy was made,
# Then there is no incremental revision, so quit with a graceful error
# message
if int(last_youngest) == int(youngest):
  print("No new revisions since original hotcopy was made.\n" + 
         "Cannot produce an incremental dump file - Exiting.\n")
  sys.exit(0)

f_out = open(backup_dump, 'wb')

print("Backing up repository to '" + backup_dump + "'...")
err_code = subprocess.call([svnadmin, "dump", "--incremental", "-r", 
                            str(int(last_youngest) + 1) + ":" + youngest, 
                            repo_dir], stdout=f_out)
f_out.close()


if err_code != 0:
  sys.stderr.write("Unable to backup the repository.\n")
  sys.stderr.flush()
  sys.exit(err_code)
else:
  print("Done.")


### Step 6: Make an archive of the backup if required.
if archive_type:
  archive_path = backup_dump + archive_map[archive_type]
  err_msg = ""

  print("Archiving backup to '" + archive_path + "'...")
  # optionally archive the hotcopy
  if archive_type:
    import tarfile
    tar = tarfile.open(archive_path, "w:"+archive_type)
    tar.add(backup_dump, arcname=repo + "-" + youngest)
    tar.close()

  print("Archive created, removing backup dumpfile '" + backup_dump + "'...")
  os.chmod(backup_dump, stat.S_IRUSR|stat.S_IWUSR)
  os.remove(backup_dump)
  print("Done")
  sys.exit(0)

