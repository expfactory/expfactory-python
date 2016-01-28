/* EXPERIMENT TEMPLATE
This is the code for the simple_rt task, which demonstrates how you should organize
your experiments. You might have a section for helper functions, experiment variables,
and jsPsych blocks. A few best practice rules:


The variable for the experiment (at the end of the script) should be named like:

      [exp_id]_experiment

where "exp_id" corresponds with the folder name and is specified as the "exp_id" variable in the config.json


Images / sounds / etc linked in this file should follow the format

      /static/experiments/[exp_id]/myimage.png

You can make any subfolders / hierarchy of files within this folder, and
they will be included.

JsPsych provides great documentation and examples:

http://docs.jspsych.org/tutorials/go-nogo-task/

After you install expfactory

      sudo pip install expfactory


You can cd into a folder like this and test your experiment in the browser

      expfactory --preview

and see our documentation for help and best practices

      expfactory.github.io/docs

/*


/* *********************************************************************************************************************
/* Define helper functions */
/* ************************************ */
var post_trial_gap = function() {
  return gap;
}

/* Append gap and current trial to data and then recalculate for next trial*/
var appendData = function() {
	gap = Math.floor( Math.random() * 2000 ) + 1000
	jsPsych.data.addDataToLastTrial({ITT: gap, trial_num: current_trial})
	current_trial = current_trial + 1
}

/* *********************************************************************************************************************
/* Define experimental variables */
/* ************************************ */
var practice_len = 5
var experiment_len = 50
var gap = 0
var current_trial = 0
stim = '<div class = shapebox><div id = cross></div></div>'



/* *********************************************************************************************************************
/* Set up jsPsych blocks */
/* 
/* Generally, an experiment has a welcome block, instructions, and then some combination of practice / test / end blocks. 
/* 
/* ************************************ */
/* define static blocks */
var welcome_block = {
  type: 'text',
  text: '<div class = centerbox><p class = block-text>Welcome to the simple RT experiment. Press <strong>enter</strong> to begin.</p></div>',
  cont_key: 13,
  timing_post_trial: 0
};

var end_block = {
  type: 'text',
  text: '<div class = centerbox><p class = center-block-text>Finished with this task.</p><p class = center-block-text>Press <strong>enter</strong> to continue.</p></div>',
  cont_key: 13,
  timing_post_trial: 0
};

var instructions_block = {
  type: 'instructions',
  pages: ['<div class = centerbox><p class = block-text>In this experiment, we are testing how fast you can respond. On each trial press the spacebar as quickly as possible <strong>after</strong> you see the large "X".</p></div>'],
  allow_keys: false,
  show_clickable_nav: true,
  timing_post_trial: 1000
};

var start_practice_block = {
  type: 'text',
  text: '<div class = centerbox><p class = center-block-text>We will start 5 practice trials. Press <strong>enter</strong> to begin.</p></div>',
  cont_key: 13,
  timing_post_trial: 1000
};

var start_test_block = {
  type: 'text',
  text: '<div class = centerbox><p class = block-text>We will now start the test. Respond to the "X" as quickly as possible by pressing the spacebar. Press <strong>enter</strong> to begin.</p></div>',
  cont_key: 13,
  timing_post_trial: 1000
};

var reset_block = {
	type: 'call-function',
	func: function() {
		current_trial = 0
	},
	timing_post_trial: 0
}

/* define practice block */
var practice_block = {
  type: 'single-stim',
  stimuli: stim,
  is_html: true,
  data: {exp_id: "simple_rt", trial_id: "practice"},
  choices: [32],
  timing_post_trial: post_trial_gap,
  on_finish: appendData,
  repetitions: practice_len
};

/* define test block */
var test_block = {
  type: 'single-stim',
  stimuli: stim,
  is_html: true,
  data: {exp_id: "simple_rt", trial_id: "test"},
  choices: [32],
  timing_post_trial: post_trial_gap,
  on_finish: appendData,
  repetitions: experiment_len
};

/* create experiment definition array */
var experiment_template_experiment = [];
experiment_template_experiment.push(welcome_block);
experiment_template_experiment.push(instructions_block);
experiment_template_experiment.push(start_practice_block);
experiment_template_experiment.push(practice_block);
experiment_template_experiment.push(reset_block)
experiment_template_experiment.push(start_test_block);
experiment_template_experiment.push(test_block);
experiment_template_experiment.push(end_block);
