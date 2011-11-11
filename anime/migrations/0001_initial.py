# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Genre'
        db.create_table('anime_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
        ))
        db.send_create_signal('anime', ['Genre'])

        # Adding model 'Credit'
        db.create_table('anime_credit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('anime', ['Credit'])

        # Adding model 'AnimeBundle'
        db.create_table('anime_animebundle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('anime', ['AnimeBundle'])

        # Adding model 'AnimeItemAuditLogEntry'
        db.create_table('anime_animeitemauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('releaseType', self.gf('django.db.models.fields.IntegerField')()),
            ('episodesCount', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('releasedAt', self.gf('django.db.models.fields.DateTimeField')()),
            ('releasedKnown', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('endedAt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('endedKnown', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('bundle', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_animeitems', null=True, to=orm['anime.AnimeBundle'])),
            ('air', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_animeitem_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeItemAuditLogEntry'])

        # Adding model 'AnimeItem'
        db.create_table('anime_animeitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('releaseType', self.gf('django.db.models.fields.IntegerField')()),
            ('episodesCount', self.gf('django.db.models.fields.IntegerField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('releasedAt', self.gf('django.db.models.fields.DateTimeField')()),
            ('releasedKnown', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('endedAt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('endedKnown', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('bundle', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='animeitems', null=True, to=orm['anime.AnimeBundle'])),
            ('air', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeItem'])

        # Adding M2M table for field genre on 'AnimeItem'
        db.create_table('anime_animeitem_genre', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('animeitem', models.ForeignKey(orm['anime.animeitem'], null=False)),
            ('genre', models.ForeignKey(orm['anime.genre'], null=False))
        ))
        db.create_unique('anime_animeitem_genre', ['animeitem_id', 'genre_id'])

        # Adding model 'AnimeEpisodeAuditLogEntry'
        db.create_table('anime_animeepisodeauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_animeepisodes', to=orm['anime.AnimeItem'])),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_animeepisode_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeEpisodeAuditLogEntry'])

        # Adding model 'AnimeEpisode'
        db.create_table('anime_animeepisode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='animeepisodes', to=orm['anime.AnimeItem'])),
        ))
        db.send_create_signal('anime', ['AnimeEpisode'])

        # Adding unique constraint on 'AnimeEpisode', fields ['title', 'anime']
        db.create_unique('anime_animeepisode', ['title', 'anime_id'])

        # Adding model 'AnimeNameAuditLogEntry'
        db.create_table('anime_animenameauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_animenames', to=orm['anime.AnimeItem'])),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_animename_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeNameAuditLogEntry'])

        # Adding model 'AnimeName'
        db.create_table('anime_animename', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='animenames', to=orm['anime.AnimeItem'])),
        ))
        db.send_create_signal('anime', ['AnimeName'])

        # Adding unique constraint on 'AnimeName', fields ['title', 'anime']
        db.create_unique('anime_animename', ['title', 'anime_id'])

        # Adding model 'AnimeLinkAuditLogEntry'
        db.create_table('anime_animelinkauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_links', to=orm['anime.AnimeItem'])),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=100)),
            ('linkType', self.gf('django.db.models.fields.IntegerField')()),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_animelink_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeLinkAuditLogEntry'])

        # Adding model 'AnimeLink'
        db.create_table('anime_animelink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['anime.AnimeItem'])),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=100)),
            ('linkType', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('anime', ['AnimeLink'])

        # Adding unique constraint on 'AnimeLink', fields ['link', 'anime']
        db.create_unique('anime_animelink', ['link', 'anime_id'])

        # Adding model 'AnimeLinksAuditLogEntry'
        db.create_table('anime_animelinksauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_links1', to=orm['anime.AnimeItem'])),
            ('AniDB', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ANN', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('MAL', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_animelinks_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['AnimeLinksAuditLogEntry'])

        # Adding model 'AnimeLinks'
        db.create_table('anime_animelinks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links1', to=orm['anime.AnimeItem'])),
            ('AniDB', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ANN', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('MAL', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('anime', ['AnimeLinks'])

        # Adding model 'OrganisationAuditLogEntry'
        db.create_table('anime_organisationauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_organisation_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['OrganisationAuditLogEntry'])

        # Adding model 'Organisation'
        db.create_table('anime_organisation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('anime', ['Organisation'])

        # Adding model 'OrganisationBundleAuditLogEntry'
        db.create_table('anime_organisationbundleauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_organisationbundles', to=orm['anime.AnimeItem'])),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_organisationbundles', to=orm['anime.Organisation'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['anime.Credit'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_organisationbundle_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['OrganisationBundleAuditLogEntry'])

        # Adding model 'OrganisationBundle'
        db.create_table('anime_organisationbundle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='organisationbundles', to=orm['anime.AnimeItem'])),
            ('organisation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='organisationbundles', to=orm['anime.Organisation'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['anime.Credit'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('anime', ['OrganisationBundle'])

        # Adding unique constraint on 'OrganisationBundle', fields ['anime', 'organisation', 'job', 'role']
        db.create_unique('anime_organisationbundle', ['anime_id', 'organisation_id', 'job_id', 'role'])

        # Adding model 'PeopleAuditLogEntry'
        db.create_table('anime_peopleauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_people_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['PeopleAuditLogEntry'])

        # Adding model 'People'
        db.create_table('anime_people', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('anime', ['People'])

        # Adding model 'PeopleBundleAuditLogEntry'
        db.create_table('anime_peoplebundleauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_peoplebundles', to=orm['anime.AnimeItem'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_peoplebundles', to=orm['anime.People'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['anime.Credit'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_peoplebundle_audit_log_entry', null=True, to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('anime', ['PeopleBundleAuditLogEntry'])

        # Adding model 'PeopleBundle'
        db.create_table('anime_peoplebundle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='peoplebundles', to=orm['anime.AnimeItem'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(related_name='peoplebundles', to=orm['anime.People'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['anime.Credit'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('anime', ['PeopleBundle'])

        # Adding unique constraint on 'PeopleBundle', fields ['anime', 'person', 'job', 'role']
        db.create_unique('anime_peoplebundle', ['anime_id', 'person_id', 'job_id', 'role'])

        # Adding model 'UserStatusBundle'
        db.create_table('anime_userstatusbundle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statusbundles', to=orm['anime.AnimeItem'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('anime', ['UserStatusBundle'])

        # Adding unique constraint on 'UserStatusBundle', fields ['anime', 'user']
        db.create_unique('anime_userstatusbundle', ['anime_id', 'user_id'])

        # Adding model 'AnimeRequest'
        db.create_table('anime_animerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('anime', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='requests', null=True, to=orm['anime.AnimeItem'])),
            ('requestType', self.gf('django.db.models.fields.IntegerField')()),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('anime', ['AnimeRequest'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'UserStatusBundle', fields ['anime', 'user']
        db.delete_unique('anime_userstatusbundle', ['anime_id', 'user_id'])

        # Removing unique constraint on 'PeopleBundle', fields ['anime', 'person', 'job', 'role']
        db.delete_unique('anime_peoplebundle', ['anime_id', 'person_id', 'job_id', 'role'])

        # Removing unique constraint on 'OrganisationBundle', fields ['anime', 'organisation', 'job', 'role']
        db.delete_unique('anime_organisationbundle', ['anime_id', 'organisation_id', 'job_id', 'role'])

        # Removing unique constraint on 'AnimeLink', fields ['link', 'anime']
        db.delete_unique('anime_animelink', ['link', 'anime_id'])

        # Removing unique constraint on 'AnimeName', fields ['title', 'anime']
        db.delete_unique('anime_animename', ['title', 'anime_id'])

        # Removing unique constraint on 'AnimeEpisode', fields ['title', 'anime']
        db.delete_unique('anime_animeepisode', ['title', 'anime_id'])

        # Deleting model 'Genre'
        db.delete_table('anime_genre')

        # Deleting model 'Credit'
        db.delete_table('anime_credit')

        # Deleting model 'AnimeBundle'
        db.delete_table('anime_animebundle')

        # Deleting model 'AnimeItemAuditLogEntry'
        db.delete_table('anime_animeitemauditlogentry')

        # Deleting model 'AnimeItem'
        db.delete_table('anime_animeitem')

        # Removing M2M table for field genre on 'AnimeItem'
        db.delete_table('anime_animeitem_genre')

        # Deleting model 'AnimeEpisodeAuditLogEntry'
        db.delete_table('anime_animeepisodeauditlogentry')

        # Deleting model 'AnimeEpisode'
        db.delete_table('anime_animeepisode')

        # Deleting model 'AnimeNameAuditLogEntry'
        db.delete_table('anime_animenameauditlogentry')

        # Deleting model 'AnimeName'
        db.delete_table('anime_animename')

        # Deleting model 'AnimeLinkAuditLogEntry'
        db.delete_table('anime_animelinkauditlogentry')

        # Deleting model 'AnimeLink'
        db.delete_table('anime_animelink')

        # Deleting model 'AnimeLinksAuditLogEntry'
        db.delete_table('anime_animelinksauditlogentry')

        # Deleting model 'AnimeLinks'
        db.delete_table('anime_animelinks')

        # Deleting model 'OrganisationAuditLogEntry'
        db.delete_table('anime_organisationauditlogentry')

        # Deleting model 'Organisation'
        db.delete_table('anime_organisation')

        # Deleting model 'OrganisationBundleAuditLogEntry'
        db.delete_table('anime_organisationbundleauditlogentry')

        # Deleting model 'OrganisationBundle'
        db.delete_table('anime_organisationbundle')

        # Deleting model 'PeopleAuditLogEntry'
        db.delete_table('anime_peopleauditlogentry')

        # Deleting model 'People'
        db.delete_table('anime_people')

        # Deleting model 'PeopleBundleAuditLogEntry'
        db.delete_table('anime_peoplebundleauditlogentry')

        # Deleting model 'PeopleBundle'
        db.delete_table('anime_peoplebundle')

        # Deleting model 'UserStatusBundle'
        db.delete_table('anime_userstatusbundle')

        # Deleting model 'AnimeRequest'
        db.delete_table('anime_animerequest')


    models = {
        'anime.animebundle': {
            'Meta': {'object_name': 'AnimeBundle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'anime.animeepisode': {
            'Meta': {'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeEpisode'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animeepisodes'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeepisodeauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeEpisodeAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animeepisode_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animeepisodes'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeitem': {
            'Meta': {'ordering': "['title']", 'object_name': 'AnimeItem'},
            'air': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'animeitems'", 'null': 'True', 'to': "orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['anime.Genre']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animeitemauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeItemAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animeitem_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'air': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_animeitems'", 'null': 'True', 'to': "orm['anime.AnimeBundle']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'endedAt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'endedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'episodesCount': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'releaseType': ('django.db.models.fields.IntegerField', [], {}),
            'releasedAt': ('django.db.models.fields.DateTimeField', [], {}),
            'releasedKnown': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.animelink': {
            'Meta': {'unique_together': "(('link', 'anime'),)", 'object_name': 'AnimeLink'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {})
        },
        'anime.animelinkauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeLinkAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animelink_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_links'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'linkType': ('django.db.models.fields.IntegerField', [], {}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'anime.animelinks': {
            'ANN': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'AniDB': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'MAL': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'AnimeLinks'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links1'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'anime.animelinksauditlogentry': {
            'ANN': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'AniDB': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'MAL': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeLinksAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animelinks_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_links1'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'anime.animename': {
            'Meta': {'ordering': "['title']", 'unique_together': "(('title', 'anime'),)", 'object_name': 'AnimeName'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'animenames'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'anime.animenameauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'AnimeNameAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_animename_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_animenames'", 'to': "orm['anime.AnimeItem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'anime.animerequest': {
            'Meta': {'object_name': 'AnimeRequest'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'requests'", 'null': 'True', 'to': "orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'requestType': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'anime.credit': {
            'Meta': {'object_name': 'Credit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.genre': {
            'Meta': {'ordering': "['name']", 'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'anime.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.organisationauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'OrganisationAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_organisation_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.organisationbundle': {
            'Meta': {'unique_together': "(('anime', 'organisation', 'job', 'role'),)", 'object_name': 'OrganisationBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organisationbundles'", 'to': "orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.organisationbundleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'OrganisationBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_organisationbundle_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_organisationbundles'", 'to': "orm['anime.Organisation']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.people': {
            'Meta': {'object_name': 'People'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'anime.peopleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'PeopleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_people_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'anime.peoplebundle': {
            'Meta': {'unique_together': "(('anime', 'person', 'job', 'role'),)", 'object_name': 'PeopleBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'peoplebundles'", 'to': "orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.peoplebundleauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'PeopleBundleAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_peoplebundle_audit_log_entry'", 'null': 'True', 'to': "orm['auth.User']"}),
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': "orm['anime.AnimeItem']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['anime.Credit']"}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_peoplebundles'", 'to': "orm['anime.People']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'anime.userstatusbundle': {
            'Meta': {'unique_together': "(('anime', 'user'),)", 'object_name': 'UserStatusBundle'},
            'anime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statusbundles'", 'to': "orm['anime.AnimeItem']"}),
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['anime']
