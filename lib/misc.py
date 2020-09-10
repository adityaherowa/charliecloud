# Subcommands not exciting enough for their own module.

import argparse
import os
import sys

import charliecloud as ch
import version


## argparse "actions" ##

class Action_Exit(argparse.Action):

   def __init__(self, *args, **kwargs):
      super().__init__(nargs=0, *args, **kwargs)

class Dependencies(Action_Exit):

   def __call__(self, *args, **kwargs):
      ch.dependencies_check()
      sys.exit(0)

class Version(Action_Exit):

   def __call__(self, *args, **kwargs):
      print(version.VERSION)
      sys.exit(0)


## Plain functions ##

# Argument: command line arguments Namespace. Do not need to call sys.exit()
# because caller manages that.

def list_(cli):
   ch.dependencies_check()
   imgdir = cli.storage + '/img'
   imgs = ch.ossafe(os.listdir, "can't list directory: %s" % imgdir, imgdir)
   for img in sorted(imgs):
      print(ch.Image_Ref(img))

def pull(cli):
   ch.dependencies_check()
   # Where does it go?
   dlcache = cli.storage + "/dlcache"
   if (cli.image_dir is not None):
      unpack_dir = cli.image_dir
      image_subdir = ""
   else:
      unpack_dir = cli.storage + "/img"
      image_subdir = None  # infer from image ref
   # Set things up.
   ref = ch.Image_Ref(cli.image_ref)
   if (cli.parse_only):
      print(ref.as_verbose_str)
      sys.exit(0)
   image = ch.Image(ref, dlcache, unpack_dir, image_subdir)
   ch.INFO("pulling image:   %s" % image.ref)
   if (cli.image_dir is not None):
      ch.INFO( "destination:     %s" % image.unpack_path)
   else:
      ch.DEBUG("destination:     %s" % image.unpack_path)
   ch.DEBUG("use cache:       %s" % (not cli.no_cache))
   ch.DEBUG("download cache:  %s" % image.download_cache)
   ch.DEBUG("manifest:        %s" % image.manifest_path)
   # Pull!
   image.pull_to_unpacked(use_cache=(not cli.no_cache))
   # Done.
   ch.INFO("done")

def push(cli):
   ch.dependencies_check()
   dlcache = cli.storage + "/dlcache"
   if (cli.local_image_dir is not None):
      image_dir = cli.local_image_dir
   else:
      image_dir = cli.storage + "/img"
   # Stage upload.
   image_ref = ch.Image_Ref(cli.local_image_ref)
   image_manifest = str(image_ref) + ".manifest.json"
   image_path = os.path.join(image_dir, image_ref.for_path)
   if (not os.path.isdir(image_path)):
      ch.FATAL("local image '%s' not found" % image_path)
   # FIXME: If we have an existing manifest, we should use it.
   if (os.path.isfile(os.path.join(dlcache, image_manifest))):
      ch.FATAL("FIXME: local image manifest '%s%s' found; use it?"
               % (dlcache, image_manifest))
   if (cli.dest_image_ref):
      dest_image_ref = ch.Image_Ref(cli.dest_image_ref)
      dest_image_ref.defaults_add()
   else:
      dest_image_ref = image_ref
   dest_image_ref.defaults_add()
   ch.INFO("pushing image:   %s" % image_ref)
   ch.INFO("destination:     https://%s" % dest_image_ref)
   upload = ch.Image_Upload(image_path, dest_image_ref)
   upload.archive_image(image_path, dlcache)
   upload.push_to_repo()

def storage_path(cli):
   print(cli.storage)

